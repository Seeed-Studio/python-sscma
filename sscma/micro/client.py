import re
import json
import string
import random
import logging
from threading import Thread, Event, Lock, current_thread
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
        """
        Initializes a Listener object.

        Args:
        - command: The command associated with the listener.
        - event: The event object associated with the listener.
        - response: The response received from the device.
        """
        self.name = command[3:].split("=")[0]
        self.event = event
        self.response = response

    def __repr__(self):
        """
        Returns a string representation of the Listener object.
        """
        return "Listener(name={}, event={}, response={})".format(
            self.name,
            self.event,
            self.response
        )


class Client:
    """
    Client class for sending and receiving messages to and from a device.

    Attributes:
    - on_write: Function that is called when a message is sent to the device.
    - on_event: Function that is called when an event is triggered.
    - on_log: Function that is called for logging purposes.
    - timeout: Timeout value for waiting for a response from the device.
    - try_count: Number of times to try sending a command to the device.
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
        Initializes the Client class.

        Args:
        - on_write: Function that is called when a message is sent to the device.
        - on_event: Function that is called when an event is triggered.
        - on_log: Function that is called for logging purposes.
        - timeout: Timeout value for waiting for a response from the device.
        - try_count: Number of times to try sending a command to the device.
        """
        self._on_write = on_write
        self._on_event = on_event
        self._on_log = on_log

        self._timeout = timeout if timeout is not None else self._timeout
        self._try_count = try_count if try_count is not None else self._try_count

        self._msg_buffer = b''
        self._listeners: List[Listener] = []

        self._lock = Lock()

    @property
    def on_write(self):
        """
        If implemented, this function will be called when a message is sent to the device.
        """
        return self._on_write

    @on_write.setter
    def on_write(self, value):
        """
        Sets the on_write function.

        Args:
        - value: The function to be set as the on_write function.
        """
        self._on_write = value

    @property
    def on_event(self):
        """
        If implemented, this function will be called when an event is triggered.
        """
        return self._on_event

    @on_event.setter
    def on_event(self, value):
        """
        Sets the on_event function.

        Args:
        - value: The function to be set as the on_event function.
        """
        self._on_event = value

    @property
    def on_log(self):
        """
        If implemented, this function will be called for logging purposes.
        """
        return self._on_log

    @on_log.setter
    def on_log(self, value):
        """
        Sets the on_log function.

        Args:
        - value: The function to be set as the on_log function.
        """
        self._on_log = value

    def _send(self, msg):
        """
        Sends a message to the device using the on_write function.

        Args:
        - msg: The message to be sent to the device.
        """
        with self._lock:
            if self._on_write is not None:
                self._on_write(msg)

    def _generate_tag(self):
        """
        Generates a random tag for a message.

        Returns:
        - tag: A string of 6 random uppercase letters and digits.
        """
        tag = ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=6))
        return tag

    def send_command(self, command, wait_event=True, timeout=None):
        """
        Sends a command to the device and waits for a response.

        Args:
        - command: The command to be sent to the device.
        - wait_event: Whether to wait for an event to be triggered.
        - timeout: Timeout value for waiting for a response from the device.

        Returns:
        - response: The response received from the device.
        """
        listener = Listener(command, Event(), None)

        for i in range(self._try_count):
            _LOGGER.debug(
                "send_command:{} try:{}/{}".format(command, i+1, self._try_count))

            if wait_event:
                listener.event.clear()
                self._listeners.append(listener)

            self._send('{}\r\n'.format(command).encode('utf-8'))

            if wait_event:
                if timeout is not None:
                    listener.event.wait(timeout)
                else:
                    listener.event.wait(self._timeout)
                # remove listener
                self._listeners.remove(listener)

            if not wait_event or listener.response is not None:
                break

        return listener.response

    def set(self, command, value, tag=True, wait_event=True, timeout=None):
        """
        Sets a value for a command on the device.

        Args:
        - command: The command to be set.
        - value: The value to be set for the command.
        - tag: Whether to add a tag to the command.
        - wait_event: Whether to wait for an event to be triggered.
        - timeout: Timeout value for waiting for a response from the device.

        Returns:
        - response: The response received from the device.
        """

        if tag:
            command = "{}{}@{}={}".format(CMD_PREFIX,
                                          self._generate_tag(), command, value)
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
        - command: The command to be queried.
        - tag: Whether to add a tag to the command.
        - wait_event: Whether to wait for an event to be triggered.
        - timeout: Timeout value for waiting for a response from the device.

        Returns:
        - response: The response received from the device.
        """
        if tag:
            command = "{}{}@{}?".format(CMD_PREFIX,
                                        self._generate_tag(), command)
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
                                       self._generate_tag(), command)
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
        self._msg_buffer += msg

        matches = re.findall(b'\r{.*}\n', self._msg_buffer)

        if matches is None or len(matches) == 0:
            return

        for match in matches:
            try:
                paylod = json.loads(match.decode('utf-8'))
                # response frame
                if "type" in paylod and paylod["type"] == CMD_TYPE_RESPONSE:
                    if "name" in paylod:
                        for listener in self._listeners:
                            if listener.name == paylod["name"]:
                                listener.response = paylod
                                listener.event.set()
                                _LOGGER.debug(
                                    "response:{}".format(paylod))

                if "type" in paylod and paylod["type"] == CMD_TYPE_EVENT:
                    if self._on_event is not None:
                        self._on_event(paylod)

                if "type" in paylod and paylod["type"] == CMD_TYPE_LOG:
                    if "name" in paylod:
                        if paylod["name"] == LOG_AT:
                            for listener in self._listeners:
                                if listener.name in paylod["data"]:
                                    listener.response = paylod
                                    listener.event.set()
                                    _LOGGER.debug(
                                        "response:{}".format(paylod))
                        if paylod["name"] == LOG_LOG:
                            if self._on_log is not None:
                                self._on_log(paylod)

            except Exception as ex:
                _LOGGER.error("payload decode exception:{}".format(ex))

            finally:
                self._msg_buffer = self._msg_buffer[self._msg_buffer.find(
                    RESPONSE_SUFFIX)+2:]


class SerialClient(Client):
    import serial as serial

    def __init__(self, port, baudrate=921600, timeout=0.1, **kwargs):

        self._serial = self.serial.Serial(
            port, baudrate, timeout=timeout,  **kwargs)
        self._running = False
        self._thread = None
        super().__init__(self._serial.write)

    def _recieve_thread(self):
        while self._running:
            if self._serial.in_waiting:
                msg = self._serial.read(self._serial.in_waiting)
                if msg != b'':
                    self.on_recieve(msg)
        self._running = False
        self._thread = None
        self._serial.close()

    def connect(self):
        if not self._serial.is_open:
            self._serial.open()

    def disconnect(self):
        if self._serial.is_open:
            self._serial.close()
    
    @property
    def is_connected(self):
        return self._serial.is_open

    def loop_start(self):
        if not self._serial.is_open:
            self._serial.open()

        if not self._running:
            self._running = True
            self._thread = Thread(
                target=self._recieve_thread)
            self._thread.start()

    def loop_stop(self):
        if self._thread is None:
            return

        self._running = False
        if current_thread() != self._thread:
            self._thread.join()
            self._thread = None


class MQTTClient(Client):
    import paho.mqtt.client as mqtt

    def __init__(self, host="localhost", port=1883, tx_topic="#", rx_topic="#", **kwargs):

        self._client = self.mqtt.Client()
        self._tx_topic = tx_topic
        self._rx_topic = rx_topic
        self._client.on_message = self.__on_recieve
        self._client.on_connect = self.__on_connect
        self._host = host
        self._port = port

        for key in kwargs:
            if key == "username":
                self._client.username_pw_set(
                    kwargs["username"], kwargs["password"])
                break

        self._client.connect(self._host, self._port, 60)
        super().__init__(lambda msg: self._client.publish(self._tx_topic, msg))

    def __on_recieve(self, client, userdata, msg):
        self.on_recieve(msg.payload)

    def __on_connect(self, client, userdata, flags, rc):
        self._client.subscribe(self._rx_topic)
        
    @property
    def is_connected(self):
        return self._client.is_connected()

    def connect(self):
        self._client.connect(self._host, self._port, 60)
        
    def disconnect(self):
        self._client.disconnect()

    def loop_start(self):
        self._client.loop_start()

    def loop_stop(self):
        self._client.loop_stop()
        self._client.disconnect()
