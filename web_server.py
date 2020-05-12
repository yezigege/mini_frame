import re
import time
import socket
import multiprocessing

import mini_frame


class WSGIServer(object):
    def __init__(self):
        # 1. 创建套接字
        self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #  设置当服务器先close 即服务器端4次挥手之后资源能够立即释放，这样就保证了，下次运行程序时 可以立即绑定指定端口，便于调试
        self.tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # 2. 绑定套接字
        self.tcp_server_socket.bind(("", 7890))

        # 3. 监听套接字
        self.tcp_server_socket.listen(128)

    def service_client(self, new_socket):
        """为客户端返回数据"""

        # 1. 接收浏览器发过来的数据，即 HTTP 请求
        # GET / HTTP/1.1
        # ...
        request = new_socket.recv(1024).decode("utf-8")

        request_lines = request.splitlines()
        print("=" * 50)
        print(request_lines)

        # GET /index.html HTTP/1.1
        # get post put del
        file_name = ""
        ret = re.match(r"[^/]+(/[^ ]*)", request_lines[0])
        if ret:
            file_name = ret.group(1)
            if file_name == "/":
                file_name = "/index.html"

        # 2. 返回 http 格式的数据，给浏览器
        # 2.1 如果请求的资源不是以 .py 结尾，那么就认为是静态资源(html/css/js/png, jpg等)
        if not file_name.endswith(".py"):
            try:
                f = open("./html" + file_name, "rb")
            except:
                response = "HTTP/1.1 404 NOT FOUND\r\n"
                response += "\r\n"
                response += "============file not found============"
                new_socket.send(response.encode("utf-8"))
            else:
                html_content = f.read()
                f.close()
                # 2.1.1 准备发送给浏览器的数据--header
                response = "HTTP/1.1 200 OK\r\n"
                response += "\r\n"
                # 2.1.2 准备发送给浏览器的数据--body
                # response += "<body><h1>天不生我李淳罡，剑道万古长如夜</h1></body>"

                # 将 response header 发送给浏览器
                new_socket.send(response.encode("utf-8"))
                # 将 response body 发送给浏览器
                new_socket.send(html_content)
        else:
            # 2.2 如果是以 .py 结尾，那么就认为是动态资源的请求
            header = "HTTP/1.1 200 OK\r\n"
            header += "\r\n"

            if file_name == "/login.py":
                body = mini_frame.login()
            elif file_name == "/register.py":
                body = mini_frame.register()
            else:
                body = f"<body><h2>this is test file{time.ctime()}</h2></body>"

            response = header + body
            # 发送 response 给浏览器
            new_socket.send(response.encode("utf-8"))

        # 关闭套接字
        new_socket.close()

    def run_forever(self):
        """用来完成整体的控制"""

        while True:
            # 4. 等待新客户端的链接
            new_socket, client_addr = self.tcp_server_socket.accept()

            # 5. 为这个客户单服务【多进程方式】
            p = multiprocessing.Process(target=self.service_client, args=(new_socket,))
            p.start()

        # 关闭监听套接字
        self.tcp_server_socket.close()


def main():
    """控制整体，创建一个 web 服务器对象，然后调用这个对象的 run_forever 方法运行"""
    wsgi_server = WSGIServer()
    wsgi_server.run_forever()


if __name__ == '__main__':
    main()
