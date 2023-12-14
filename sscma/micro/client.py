import re
import json
import string
import random
import logging
import serial
from threading import Thread, Event, Lock
from typing import List, Optional  # noqa: F401

from .const import *

_LOGGER = logging.getLogger(__name__)


class Listener:
    """
    Represents a listener for events triggered by the device.

    Attributes:
    - name: The name of the listener.
    - event: The event object associated with the listener.
    - response: The response received from the device.
    """

    def __init__(self, command, event, response=None):
        self.name = command[3:].split("=")[0]
        self.event = event
        self.response = response

    def __repr__(self):
        return "Listener(name={}, event={}, response={})".format(
            self.name,
            self.event,
            self.response
        )


class Client:
    """
    Client class for sending and receiving messages to and from a device.

    Attributes:
    """
    _timeout: int = 10
    _try_count: int = 3

    def __init__(self,
                 on_write=None,
                 on_event=None,
                 on_log=None,
                 timeout: Optional[int] = None,
                 try_count: Optional[int] = None,
                 ) -> None:
        """
        Initializes the Client class with a send_handler function.

        Args:
        - send_handler: function that sends messages to the device.
        """
        self.on_write = on_write
        self.on_event = on_event
        self.on_log = on_log

        self.__timeout = timeout if timeout is not None else self._timeout
        self.__try_count = try_count if try_count is not None else self._try_count

        self.__msg_buffer = b''
        self.__listeners: List[Listener] = []

        self.__lock = Lock()

    def __send(self, msg):
        """
        Sends a message to the device using the on_write function.

        Args:
        - msg: message to be sent to the device.
        """
        with self.__lock:
            if self.on_write is not None:
                self.on_write(msg)

    def __generate_tag(self):
        """
        Generates a random tag for a message.

        Returns:
        - tag: a string of 6 random uppercase letters and digits.
        """
        tag = ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=6))
        return tag

    def send_command(self, command, wait_event=True, timeout=None):
        """
        Sends a command to the device and waits for a response.

        Args:
        - command: command to be sent to the device.
        - wait_event: whether to wait for an event to be triggered.

        Returns:
        - response: response received from the device.
        """
        listener = Listener(command, Event(), None)

        for i in range(self.__try_count):
            _LOGGER.debug(
                "send_command:{} try:{}/{}".format(command, i+1, self.__try_count))

            if wait_event:
                listener.event.clear()
                self.__listeners.append(listener)

            self.__send('{}\r\n'.format(command).encode('utf-8'))

            if wait_event:
                if timeout is not None:
                    listener.event.wait(timeout)
                else:
                    listener.event.wait(self.__timeout)
                # remove listener
                self.__listeners.remove(listener)

            if not wait_event or listener.response is not None:
                break

        return listener.response

    def set(self, command, value, tag=True, wait_event=True, timeout=None):
        """
        Sets a value for a command on the device.

        Args:
        - command: command to be set.
        - value: value to be set for the command.
        - tag: whether to add a tag to the command.
        - wait_event: whether to wait for an event to be triggered.

        Returns:
        - response: response received from the device.
        """

        if tag:
            command = "{}{}@{}={}".format(CMD_PREFIX,
                                          self.__generate_tag(), command, value)
        else:
            command = "{}{}={}".format(CMD_PREFIX, command, value)

        response = self.send_command(command, wait_event, timeout)
        if response is None:
            return None
        else:
            return response

    def get(self, command, tag=True, wait_event=True, timeout=None):
        """
        Queries the value of a command on the device.

        Args:
        - command: command to be queried.
        - tag: whether to add a tag to the command.
        - wait_event: whether to wait for an event to be triggered.

        Returns:
        - response: response received from the device.
        """
        if tag:
            command = "{}{}@{}?".format(CMD_PREFIX,
                                        self.__generate_tag(), command)
        else:
            command = "{}{}?".format(CMD_PREFIX, command)

        response = self.send_command(command, wait_event, timeout)
        if response is None:
            return None
        else:
            return response

    def execute(self, command, tag=False, wait_event=False, timeout=None):
        """
        Executes a command on the device.

        Args:
        - command: command to be executed.
        - tag: whether to add a tag to the command.
        - wait_event: whether to wait for an event to be triggered.

        Returns:
        - response: response received from the device.
        """
        if tag:
            command = "{}{}@{}".format(CMD_PREFIX,
                                       self.__generate_tag(), command)
        else:
            command = "{}{}".format(CMD_PREFIX, command)

        response = self.send_command(command, wait_event, timeout)
        if response is None:
            return None
        else:
            return response

    def on_recieve(self, msg):
        """
        Handles messages received from the device

        Args:
        - msg: message received from the device.
        """
        self._recieve_handler(msg)

    def _recieve_handler(self, msg):
        """
        Handles messages received from the device

        Args:
        - msg: message received from the device.
        """
        self.__msg_buffer += msg

        matches = re.findall(b'\r{.*}\n', self.__msg_buffer)

        if matches is None or len(matches) == 0:
            return

        for match in matches:
            try:
                paylod = json.loads(match.decode('utf-8'))
                # response frame
                if "type" in paylod and paylod["type"] == CMD_TYPE_RESPONSE:
                    if "name" in paylod:
                        for listener in self.__listeners:
                            if listener.name == paylod["name"]:
                                listener.response = paylod
                                listener.event.set()
                                _LOGGER.debug(
                                    "response:{}".format(paylod))

                if "type" in paylod and paylod["type"] == CMD_TYPE_EVENT:
                    if self.on_event is not None:
                        self.on_event(paylod)

                if "type" in paylod and paylod["type"] == CMD_TYPE_LOG:
                    if "name" in paylod:
                        if paylod["name"] == LOG_AT:
                            for listener in self.__listeners:
                                if listener.name in paylod["data"]:
                                    listener.response = paylod
                                    listener.event.set()
                                    _LOGGER.debug(
                                        "response:{}".format(paylod))
                        if paylod["name"] == LOG_LOG:
                            if self.on_log is not None:
                                self.on_log(paylod)

            except Exception as ex:
                _LOGGER.error("payload decode exception:{}".format(ex))

            finally:
                self.__msg_buffer = self.__msg_buffer[self.__msg_buffer.find(
                    RESPONSE_SUFFIX)+2:]


class SerialClient(Client):
    def __init__(self, port, baudrate=921600, timeout=0.1, **kwargs):
        self.__serial = serial.Serial(port, baudrate, timeout=timeout)
        self.__running = False
        self.__thread = None
        super().__init__(self.__serial.write, **kwargs)

    def _recieve_thread(self):
        while self.__running:
            if self.__serial.in_waiting:
                msg = self.__serial.read(self.__serial.in_waiting)
                if msg != b'':
                    self._recieve_handler(msg)

    def loop_start(self):
        if not self.__running:
            self.__running = True
            self.__thread = Thread(
                target=self._recieve_thread)
            self.__thread.start()

    def loop_stop(self):
        if self.__running:
            self.__running = False
            self.__thread.join()
            self.__thread = None


