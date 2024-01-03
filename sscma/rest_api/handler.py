from typing import Tuple

import json
import threading
import logging

import socketserver
import http
from http import HTTPStatus

from supervision import Detections

from .session_manager import SessionManager
from .utils import (
    parse_bytes_to_json,
    SessionConfig,
    image_from_base64,
)

shared_session_manager = SessionManager()


class HTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(
        self,
        request: bytes,
        client_address: Tuple[str, int],
        server: socketserver.BaseServer,
    ):
        super().__init__(request, client_address, server)

    def verify_content_type(self):
        if not self.headers["Content-Type"] == "application/json":
            self.send_response(HTTPStatus.NOT_ACCEPTABLE)
            self.end_headers()
            return False
        return True

    def verify_content_length(self):
        if "Content-Length" not in self.headers:
            self.send_response(HTTPStatus.LENGTH_REQUIRED)
            self.end_headers()
            return False
        return True

    @property
    def session_id(self):
        if "Session-Id" not in self.headers:
            raise ValueError("Session-Id is required")
        session_id = str(self.headers["Session-Id"])
        if not session_id.isalnum():
            raise ValueError("Session id should be alphanumeric")
        if len(session_id) not in range(1, 32):
            raise ValueError("Session id should be between 1 and 32 chars")
        return session_id

    def do_GET(self):
        if self.path != "/":
            self.send_response(HTTPStatus.NOT_FOUND)
            self.end_headers()
            return

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        response = {}
        response["sessions"] = shared_session_manager.get_all_sessions_id()
        response["max_sessions"] = shared_session_manager.get_sessions_limit()
        response["active_threads"] = threading.active_count()

        self.wfile.write(bytes(json.dumps(response).encode()))
        self.wfile.flush()

    def do_POST(self):
        if not (self.verify_content_type() and self.verify_content_length()):
            return

        content_length = int(self.headers["Content-Length"])
        request = self.rfile.read(content_length)

        try:
            request = parse_bytes_to_json(request)

            if self.path == "/":
                session_id = self.session_id
                session_config = SessionConfig(**request)
                shared_session_manager.create_session(session_id, session_config)

                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
            else:
                session_id = self.path[1:]
                session = shared_session_manager.get_session(session_id)
                detections = Detections.from_sscma_micro(request)
                image = None
                if "image" in request:
                    try:
                        image = image_from_base64(request["image"])
                    except Exception as exc:  # pylint: disable=broad-except
                        logging.warning("Failed to parse image", exc_info=exc)
                annotations = request["annotations"] if "annotations" in request else None
                response = session.push(detections, image, annotations)

                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/json")
                self.end_headers()

                self.wfile.write(bytes(json.dumps(response).encode()))
                self.wfile.flush()

        except Exception as exc:  # pylint: disable=broad-except
            logging.warning("Failed to parse request", exc_info=exc)
            self.send_response(HTTPStatus.BAD_REQUEST)
            self.end_headers()

    def do_DELETE(self):
        if self.path != "/":
            self.send_response(HTTPStatus.NOT_FOUND)
            self.end_headers()
            return

        try:
            session_id = self.session_id
            if not shared_session_manager.remove_session(session_id):
                raise ValueError(f"Session {session_id} not exist")

        except Exception as exc:  # pylint: disable=broad-except
            logging.warning("Failed to remove session", exc_info=exc)
            self.send_response(HTTPStatus.BAD_REQUEST)
            self.end_headers()
            return

        self.send_response(HTTPStatus.OK)
        self.end_headers()
