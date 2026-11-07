"""probe.py 核心探测逻辑的单元测试。

覆盖 prob_tcp 的三个分支（对应 README 验收标准第 2 条「故障隔离」）：
  1. 端口可达      -> alive=True
  2. 端口无服务    -> alive=False + ConnectionRefusedError，不抛异常
  3. 地址不可达    -> alive=False + TimeoutError，不崩溃

用 asyncio.run() 包装异步场景，避免引入 pytest-asyncio 插件，保持依赖最小。
"""
import asyncio

import probe


async def _noop(reader, writer):
    """接受连接后立刻关闭，模拟一个「开着的端口」。"""
    writer.close()
    await writer.wait_closed()


async def _reserve_then_free_port() -> int:
    """临时起一个服务拿到空闲端口，立刻关闭后返回该端口。

    这样能保证端口「刚刚还是空的、现在没有服务监听」，
    探测它一定会得到 ConnectionRefused，测试稳定不 flaky。
    """
    server = await asyncio.start_server(_noop, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    server.close()
    await server.wait_closed()
    return port


def test_prob_tcp_alive():
    """端口可达 -> alive=True，且 host/port 与输入一致。"""

    async def scenario():
        server = await asyncio.start_server(_noop, "127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]
        try:
            result = await probe.prob_tcp("127.0.0.1", port, timeout=2.0)
        finally:
            server.close()
            await server.wait_closed()
        return result, port

    result, port = asyncio.run(scenario())
    assert result["alive"] is True
    assert result["host"] == "127.0.0.1"
    assert result["port"] == port
    assert "error" not in result


def test_prob_tcp_refused():
    """端口无服务 -> alive=False + error，且不抛异常（故障隔离）。"""

    async def scenario():
        port = await _reserve_then_free_port()
        return await probe.prob_tcp("127.0.0.1", port, timeout=2.0)

    result = asyncio.run(scenario())
    assert result["alive"] is False
    assert result["host"] == "127.0.0.1"
    assert "error" in result


def test_prob_tcp_timeout():
    """不可达地址 -> alive=False + TimeoutError，超时不崩溃。"""

    async def scenario():
        # 192.0.2.1 属 TEST-NET-1（RFC 5737）保留地址，公网不可路由，连接会超时
        return await probe.prob_tcp("192.0.2.1", 80, timeout=0.2)

    result = asyncio.run(scenario())
    assert result["alive"] is False
    # 不同环境下不可达地址可能表现为 TimeoutError 或 OSError，都算「探测失败」
    assert result["error"] in ("TimeoutError", "OSError")
