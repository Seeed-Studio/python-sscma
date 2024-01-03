import click

from sscma.cli.flahser import flasher
from sscma.cli.server import server

@click.group()
def cli():
    pass

cli.add_command(flasher)
cli.add_command(server)

def main():
    cli()

if __name__ == '__main__':
    main()
