import socket
from http.server import BaseHTTPRequestHandler, HTTPServer

COUNTER = 0

class Server(BaseHTTPRequestHandler):
    def _set_headers(self, code):
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        global COUNTER
        if COUNTER > 5:
            self._set_headers(500)
            self.wfile.write(b'Internal server error\n')
        else:
            COUNTER += 1
            self._set_headers(200)
            info = "Hello from {}:v3\n".format(socket.gethostname())
            self.wfile.write(str.encode(info))

server_address = ('', 8080)
httpd = HTTPServer(server_address, Server)
httpd.serve_forever()
