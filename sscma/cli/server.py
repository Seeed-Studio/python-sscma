import click
from sscma.rest_api.server import HTTPServer

@click.command()
@click.option('--host', default='127.0.0.1', help='Host to run the server on')
@click.option('--port', default=8000, type=int, help='Port to run the server on')
@click.option('--ssl', is_flag=True, help='Use SSL for the server')
@click.option('--ssl-certfile', default='', help='SSL certificate file')
@click.option('--ssl-keyfile', default='', help='SSL key file')
@click.option('--max-workers', default=4, type=int, help='Maximum number of worker threads')
def server(host, port, ssl, ssl_certfile, ssl_keyfile, max_workers):

    try:
        http_server = HTTPServer(host, port, ssl, ssl_certfile, ssl_keyfile, max_workers)
        http_server.serve_forever()
    except Exception as e:  # pylint: disable=broad-except
        click.echo(f"Error: {e}")
        return
