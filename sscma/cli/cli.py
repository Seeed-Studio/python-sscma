import click

from sscma.cli.flahser import flasher

@click.group()
def cli():
    pass

cli.add_command(flasher)

def main():
    cli()

if __name__ == '__main__':
    main()