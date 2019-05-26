import socket
from http.server import BaseHTTPRequestHandler, HTTPServer

class Server(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        info = "Hello from {}:v1\n".format(socket.gethostname())
        self.wfile.write(str.encode(info))

server_address = ('', 8080)
httpd = HTTPServer(server_address, Server)
httpd.serve_forever()
