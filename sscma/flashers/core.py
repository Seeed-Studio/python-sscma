import io
import time
import serial 
import logging
import secrets

from tqdm import tqdm
from xmodem import XMODEM

from sscma.flashers.base import BaseFlasher

def fnv_hash(id_full):
    hash_value = 0x811c9dc5
    prime = 0x1000193
    for value in id_full:
        hash_value ^= value
        hash_value *= prime
    return hash_value & 0xFFFFFFFF 


class HimaxFlasher(BaseFlasher):
    
    _NAME = "Himax Flasher"
    
    _USB = [{"vid": 0x1A86, "pid": 0x55D2},
            {"vid": 0x1A86, "pid": 0x55D3}]
    
    def __init__(self, port, baudrate=921600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = serial.Serial()
        self.serial.port = self.port
        self.serial.baudrate = self.baudrate
        self.serial.timeout = self.timeout
        self.xmodem = XMODEM(self.getc, self.putc, mode='xmodem')
        self.log = logging.getLogger('sscma.flasher')
        
        #logging.getLogger('xmodem.XMODEM').setLevel(logging.CRITICAL + 1)

    
        super().__init__()
        
    def name():
        return HimaxFlasher._NAME
        
    def match(port):

        for usb in HimaxFlasher._USB:
            if usb['vid'] == port.vid and usb['pid'] == port.pid:
                return True
        return False
        

    
    def getc(self, size, timeout=1):
        data = self.serial.read(size) or None
        return data
    
    def putc(self, data, timeout=1):
        return self.serial.write(data) or None
    
    
    def wait_for_bootloader(self, timeout=5000):
        rbuf = b''
        
        self.serial.timeout = 0.01
        while True:
            self.serial.write(b'1')
            rbuf += self.serial.read(128)
            if 'Xmodem download and burn FW image'.encode() in rbuf:
                rbuf = b''
                self.serial.write(b'1')
                break
            timeout -= 10
            if timeout <= 0:
                raise Exception('Timeout waiting for burn mode')
            
    def wait_for_flash(self, timeout=5000):
        self.serial.timeout = 0.01
        while True:
            if self.serial.read(1) == b'C':
                time.sleep(1)
                if self.serial.read(1) == b'C':
                    break
            timeout -= 10
            if timeout <= 0:
                raise Exception('Timeout waiting for flash')
        
    def wait_for_config_done(self, timeout=5000):
        rbuf = b''
        self.serial.timeout = 0.01
        while True:
            rbuf += self.serial.read(128)
            if 'Do you want to end file transmission and reboot system'.encode() in rbuf:
                rbuf = b''
                self.serial.write(b'n')
                break
            timeout -= 10
            if timeout <= 0:
                raise Exception('Timeout waiting for config')
            
    def wait_for_flash_done(self, timeout=10000):
        rbuf = b''
        self.serial.timeout = 0.01
        while True:
            rbuf += self.serial.read(128)
            if 'Do you want to end file transmission and reboot system'.encode() in rbuf:
                rbuf = b''
                self.serial.write(b'y')
                break
            timeout -= 10
            if timeout <= 0:
                raise Exception('Timeout waiting for completion')
    
    
    def write(self, data, offset=0x00):
        
        self.serial.open()
        
        self.wait_for_bootloader()
        
        self.wait_for_flash()
        time.sleep(1)
        self.serial.reset_input_buffer()
        
    
        if (offset != 0):
            config = bytearray(128)
            config[0] = 0xC0
            config[1] = 0x5A
            config[2] = (offset >> 0) & 0xFF
            config[3] = (offset >> 8) & 0xFF
            config[4] = (offset >> 16) & 0xFF
            config[5] = (offset >> 24) & 0xFF
            config[6] = 0x00
            config[7] = 0x00
            config[8] = 0x00
            config[9] = 0x00
            config[10] = 0x5A
            config[11] = 0xC0
            for i in range(12, 128):
                config[i] = 0xFF
            config = io.BytesIO(config)
            self.serial.timeout = 2
            status = self.xmodem.send(config, quiet=True)
        
            if not status:
                raise Exception('Failed to send config')
            
            self.wait_for_config_done()
            
            time.sleep(1)
            
        data = io.BytesIO(data)
        
        progress_bar = tqdm(total=len(data.getbuffer()), unit='B',
                            unit_scale=True, unit_divisor=1024, ncols=80)
    
        def callback_written(total_packets, success_count, error_count):
            progress_bar.update(total_packets * 128 - progress_bar.n)
        
        self.serial.timeout = 60
        self.serial.reset_input_buffer()
        status = self.xmodem.send(data, retry=60, timeout=60, quiet=False, callback=callback_written)
        
        if status:
            self.wait_for_flash_done()

        
        self.serial.close()
        time.sleep(0.5)
        self.serial.open()
        time.sleep(0.5)
        self.serial.close()
        
        progress_bar.close()
        
        
    def write_sn(self):
        random_bytes = secrets.token_bytes(4 * 1024)
        sn = str(hex(fnv_hash(random_bytes[:16])))
        self.write(random_bytes, 0x003DF000)
        return sn
        
 
        
            
            
            
            