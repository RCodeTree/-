from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import sys


# 自定义请求处理器类
class Handler(BaseHTTPRequestHandler):
    """ 处理 POST 请求 """
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0)) # 父类已经解析好的请求头，是个类似字典的对象。requests.post(..., json=results) 发请求时，requests 会自动带上 Content-Length 头，值就是 body 的字节数。取 body 长度；万一没这个头，默认 0（防御性写法）
        body = self.rfile.read(length) # self.rfile：父类准备好的「读流」（file-like 对象），指向客户端发来的请求体。.read(length) 精确读出 length 个字节——这正是 Content-Length 存在的意义：HTTP 是流式的，服务器必须知道「读多少字节才算读完一个 body」
        data = json.loads(body or b"[]")
        print(f"[收到上报] {len(data)} 条记录: {[r['host'] for r in data]}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"ok": true}') # self.wfile：跟 rfile 对应，是「写流」。write(...) 把响应体写回给客户端

    """ 关闭默认访问日志 """
    def log_message(self, *args):
        pass  # 关闭默认访问日志


""" 启动 HTTP 服务器 """
if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"mock 上报服务监听 http://127.0.0.1:{port}")
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
