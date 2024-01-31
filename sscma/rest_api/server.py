import ssl

from socketserver import ThreadingMixIn
from http import server as http_server
from concurrent.futures import ThreadPoolExecutor

from .handler import HTTPHandler


class PooledHTTPServer(ThreadingMixIn, http_server.HTTPServer):
    def __init__(
        self, server_address, RequestHandlerClass, max_workers, bind_and_activate=True
    ):
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)
        self.pool = ThreadPoolExecutor(max_workers=max_workers)

    def process_request(self, request, client_address):
        self.pool.submit(self.process_request_thread, request, client_address)


class HTTPServer:
    def __init__(
        self,
        host: str,
        port: int,
        ssl_enabled: bool,
        ssl_certfile: str,
        ssl_keyfile: str,
        max_workers: int,
    ):
        self.host = host
        self.port = port
        self.ssl_enabled = ssl_enabled
        self.ssl_certfile = ssl_certfile
        self.ssl_keyfile = ssl_keyfile
        self.max_workers = max_workers

    def serve_forever(self):
        server = PooledHTTPServer(
            (self.host, self.port), HTTPHandler, max_workers=self.max_workers
        )
        if self.ssl_enabled:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(
                certfile=self.ssl_certfile, keyfile=self.ssl_keyfile
            )
            server.socket = context.wrap_socket(server.socket, server_side=True)
        server.allow_reuse_address = True
        server.serve_forever()
