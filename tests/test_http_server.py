import argparse

from sscma.rest_api.server import HTTPServer

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default='127.0.0.1')
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--ssl", action='store_true')
    parser.add_argument("--ssl_certfile", type=str, default='')
    parser.add_argument("--ssl_keyfile", type=str, default='')
    parser.add_argument("--max_workers", type=int, default=4)
    args = parser.parse_args()

    server = HTTPServer(args.host,
                             args.port,
                             args.ssl,
                             args.ssl_certfile,
                             args.ssl_keyfile,
                             args.max_workers)
    server.serve_forever()

if __name__ == "__main__":
    main()
