# 项目03：多主机批量探活 + 并发上报

## 一、需求清单

1. **输入**：主机列表（`--hosts` 逗号分隔，或 `--hosts-file` 文件）+ 目标端口
2. **并发探测**：用 `asyncio` 做 **TCP 探活**（对 `host:port` 建连接，比 ICMP ping 更贴近云运维——很多主机禁 ping 但端口是开的）
3. **限流**：`Semaphore` 控制并发数
4. **故障隔离**：单台主机连不上，只记 `alive=False`，不影响整体
5. **输出**：汇总表格 + JSON 落盘
6. **日志**：logging 双输出
7. **上报**：把结果 POST 到服务端（复用上一课的重试逻辑，凭证走环境变量）

## 二、目录结构

```
probe/
├── README.md          # 项目需求与结构说明（本文件）
├── requirements.txt   # aiohttp, requests
├── probe.py           # 并发探测核心（TCP + 限流 + 隔离）
└── main.py            # CLI + 日志 + 汇总输出
```

## 三、运行示例

```bash
# 在 venv 中
python main.py --hosts 127.0.0.1,192.168.142.130,10.255.255.1 --port 22 --concurrency 3
# 或读文件
python main.py --hosts-file hosts.txt --port 22 -v
```

## 四、验收标准（4 条）

1. 并发探活正确，`concurrency=3` 时同时最多 3 条连接（可用日志/时间验证）；
2. **故障隔离**：多台离线主机不影响整体，全部有结果、无崩溃；
3. 结果同时打印表格 + 落盘 JSON（带时间戳）；
4. 能讲清 `Semaphore`、`asyncio.wait_for`、`gather` 各自的作用。
