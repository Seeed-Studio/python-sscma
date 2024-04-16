import click
from sscma.flashers import FLASHERS

def get_flasher_by_port(com=None):
    
    import os

    if os.name == 'nt':  # sys.platform == 'win32':
        from serial.tools.list_ports_windows import comports
    elif os.name == 'posix':
        from serial.tools.list_ports_posix import comports
    else:
        raise ImportError("Sorry: no implementation for your platform ('{}') available".format(os.name))
    
    ports = comports()

    if len(ports) == 0:
        raise Exception('No Device Found')
    
 
    if com is None:
        # 如果未指定 com 口，则让用户选择
        click.echo("Multiple COM ports detected. Please select one:")
        for idx, port in enumerate(ports):
            click.echo(f"{idx + 1}. {port.device}")
        choice = click.prompt("Enter the number of the COM port", type=int)
        selected_port = ports[choice - 1]
    else:
        for port in ports:
            if port.device == com:
                selected_port = port
                break
    
    for flasher in FLASHERS:
        if flasher.match(selected_port):
            return flasher, selected_port.device
    
    return None, None

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
