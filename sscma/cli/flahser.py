import click
from sscma.flashers.utils import get_flasher_by_port

@click.command()
@click.option('--port', '-p', default=None, help='Port to connect to')
@click.option('--file', '-f', default=None, help='File to write to the device')
@click.option('--baudrate',  '-b', default=921600, help='Baud rate for the serial connection')
@click.option('--offset', '-o', default='0x00', help='Offset to write the file to')
def flasher(port, baudrate, file, offset):
    try:
        Flasher, device = get_flasher_by_port(port)
        
        if not Flasher:
            click.echo("No flasher found. Exiting.")
            return
        
        flasher = Flasher(device, baudrate=baudrate)
        if file:
            with open(file, 'rb') as file:
                data = file.read()
                click.echo(("Found device {}. Writing file to device...").format(device))
                click.echo(("File: {}").format(file.name))
                click.echo(("Offset: {}").format(offset))
                flasher.write(data, offset=int(offset, 16))
        else:
            click.echo("No operation specified. Exiting.")
    except Exception as e:
        click.echo("Error: {}".format(e))
        return
