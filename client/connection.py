import struct
from abc import ABC, abstractmethod
from typing import Tuple

import socket

from common.command import Command, COMMAND_SIZE
from common.data import REGISTER_RESPONSE
from common.image import Image
from common import udp


class Connection(ABC):

    @abstractmethod
    def wait_for_command(self) -> Command:
        pass

    @abstractmethod
    def send_register(self) -> int:
        pass

    @abstractmethod
    def send_image(self, sender_id: int, image: Image):
        pass

    @abstractmethod
    def send_no_image(self, sender_id: int):
        pass

    @abstractmethod
    def close(self):
        pass


class UdpConnection(Connection):

    def __init__(self, skt: socket.socket, address: Tuple[str, int]):
        self._socket = skt
        self._address = address

    def wait_for_command(self) -> Command:
        data, address = self._socket.recvfrom(COMMAND_SIZE)
        return Command(data)

    def send_register(self) -> int:
        # send the server a response:
        self._socket.sendto(REGISTER_RESPONSE, self._address)

        # Receive ID and save it.
        data, address = self._socket.recvfrom(struct.calcsize('i'))
        client_id, = struct.unpack('i', data)

        return client_id

    def send_image(self, sender_id: int, image: Image):
        udp.send_image(self._socket, sender_id, self._address, image)

    def send_no_image(self, sender_id: int):
        udp.send_no_image(self._socket, sender_id, self._address)

    def close(self):
        self._socket.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return self

    @staticmethod
    def create(local_port: int, server_address: Tuple[str, int]) -> Connection:
        skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Make client blocking so we wait to receive information
        skt.setblocking(True)
        # Bind the socket to the address and port.
        skt.bind(('', local_port))

        return UdpConnection(skt, server_address)
