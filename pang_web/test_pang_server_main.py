import socket
from random import randint
from unittest import TestCase

from pang_client.pang_client_main import send_snapshot_to_server, send_score_to_server, random_name_picker


class Test(TestCase):
    def test_thread_callback(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = "localhost"
        port = 2345
        s.connect((host, port))
        print(f"DEBUG connected to {host}:{port}")
        snapshot = {
            "type": "snapshot",
            "one": "1",
            "two": 2
        }
        send_snapshot_to_server(s, snapshot)
        send_snapshot_to_server(s, snapshot)
        send_score_to_server(s, random_name_picker(), randint(100, 999))
        s.close()
