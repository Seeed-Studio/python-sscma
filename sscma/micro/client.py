import re
import json
import string
import random
import logging
from threading import Event, Lock
from typing import Any, List, Optional  # noqa: F401

from .const import *
from .exceptions import PayloadDecodeException

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
    - _msg_buffer: The buffer for storing incoming messages.
    - _listeners: The list of active listeners for events.
    - _send_handler: The function that sends messages to the device.
    - _event_handler: The function that handles events received from the device.
    - _log_handler: The function that handles log messages received from the device.
    - _timeout: The timeout value for waiting for a response from the device.
    - _try_count: The number of times to try sending a command to the device.
    - _debug: The debug level for logging.
    """

    _msg_buffer: bytes = b''
    _listeners: List[Listener] = []

    _send_handler: Any = None
    _event_handler: Any = None
    _log_handler: Any = None

    _timeout: int = 10
    _try_count: int = 3
    _debug: int = 0

    def __init__(self,
                 send_handler=None,
                 event_handler=None,
                 log_handler=None,
                 debug: int = 0,
                 timeout: Optional[int] = None,
                 try_count: Optional[int] = None,
                 ) -> None:
        """
        Initializes the Client class with a send_handler function.

        Args:
        - send_handler: function that sends messages to the device.
        """
        self._send_handler = send_handler
        self._event_handler = event_handler
        self._log_handler = log_handler

        self._timeout = timeout if timeout is not None else self._timeout
        self._try_count = try_count if try_count is not None else self._try_count

        self._debug = debug
        self._msg_buffer = b''

        self.lock = Lock()

    def set_event_handler(self, event_handler):
        """
        Sets the event handler function for the Client class.

        Args:
        - event_handler: function that handles events received from the device.
        """
        self._event_handler = event_handler

    def set_log_handler(self, log_handler):
        """
        Sets the log handler function for the Client class.

        Args:
        - log_handler: function that handles log messages received from the device.
        """
        self._log_handler = log_handler

    def _send(self, msg):
        """
        Sends a message to the device using the send_handler function.

        Args:
        - msg: message to be sent to the device.
        """
        with self.lock:
            if self._send_handler is not None:
                self._send_handler(msg)

    def _generate_tag(self):
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

        for i in range(self._try_count):
            if self._debug:
                _LOGGER.info(
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
        - command: command to be set.
        - value: value to be set for the command.
        - tag: whether to add a tag to the command.
        - wait_event: whether to wait for an event to be triggered.

        Returns:
        - response: response received from the device.
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
        - command: command to be queried.
        - tag: whether to add a tag to the command.
        - wait_event: whether to wait for an event to be triggered.

        Returns:
        - response: response received from the device.
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

    def recieve_handler(self, msg):
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
                                if self._debug:
                                    _LOGGER.info(
                                        "response:{}".format(paylod))

                if "type" in paylod and paylod["type"] == CMD_TYPE_EVENT:
                    if self._event_handler is not None:
                        self._event_handler(paylod)

                if "type" in paylod and paylod["type"] == CMD_TYPE_LOG:
                    if "name" in paylod:
                        if paylod["name"] == LOG_AT:
                            for listener in self._listeners:
                                if listener.name in paylod["data"]:
                                    listener.response = paylod
                                    listener.event.set()
                                    if self._debug:
                                        _LOGGER.info(
                                            "response:{}".format(paylod))
                        if paylod["name"] == LOG_LOG:
                            if self._log_handler is not None:
                                self._log_handler(paylod)

            except Exception as ex:
                if (self._debug):
                    _LOGGER.error("payload decode exception:{}".format(ex))

            finally:
                self._msg_buffer = self._msg_buffer[self._msg_buffer.find(
                    RESPONSE_SUFFIX)+2:]
