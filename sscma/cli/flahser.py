import traceback
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
    selected_port = None
    selected_flasher = None

    if len(ports) == 0:
        raise Exception('No Device Found')
    
 
    if com is None and len(ports) > 1:
        # if we don't specify com port, let user select one
        click.echo("Multiple COM ports detected. Please select one:")
        for idx, port in enumerate(ports):
            click.echo(f"{idx + 1}. {port.device}")
        choice = click.prompt("Enter the number of the COM port", type=int)
        selected_port = ports[choice - 1]
    else:
        for port in ports:
            selected_port = port
            if selected_port.device == com:
                break
    
    for flasher in FLASHERS:
        if flasher.match(selected_port):
            selected_flasher = flasher
            break
        
    if selected_flasher is None and selected_port is not None:
            click.echo(("Found device {}. Please select flasher.").format(selected_flasher))
            for idx, flasher in enumerate(FLASHERS):
                click.echo(f"{idx + 1}. {flasher.name()}")
                choice = click.prompt("Enter the number of the flasher", type=int)
                selected_flasher = FLASHERS[choice - 1]
            else:
                click.echo("No device found. Exiting.")
    
    return selected_flasher, selected_port.device

@click.command()
@click.option('--port', '-p', default=None, help='Port to connect to')
@click.option('--file', '-f', default=None, help='File to write to the device')
@click.option('--baudrate',  '-b', default=921600, help='Baud rate for the serial connection')
@click.option('--offset', '-o', default='0x00', help='Offset to write the file to')
@click.option('--sn', '-s', is_flag=True, default=False, help='Write serial number')
def flasher(port, baudrate, file, offset, sn):
    
    if sn is False and file is None:
        click.echo("No operation specified. Exiting.")
        exit(0)
    
    try:
        Flasher, device = get_flasher_by_port(port)
        
        if Flasher is None or device is None:
            click.echo("No device found. Exiting.")
            return
        
        flasher = Flasher(device, baudrate=baudrate)
        
        if file is not None:
            with open(file, 'rb') as file:
                data = file.read()
                click.echo(("Found device {}. Writing file to device...").format(device))
                click.echo(("File: {}").format(file.name))
                click.echo(("Offset: {}").format(offset))
                flasher.write(data, offset=int(offset, 16))
        
        if sn:            
            number = flasher.write_sn()
            click.echo(("Serial number: {}").format(number))
            
       
    except Exception as e:
        click.echo("Error: {}".format(e))
        traceback.print_exc()
        return
