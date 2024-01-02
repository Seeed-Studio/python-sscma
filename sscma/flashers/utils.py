from sscma.flashers.core import HimaxFlasher

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
 
    for port in ports:
        if com != None and port.device != com:
            continue
        if port.pid == HimaxFlasher._USB['pid'] and port.vid == HimaxFlasher._USB['vid']:
            return HimaxFlasher, port.device
    
    return None, None