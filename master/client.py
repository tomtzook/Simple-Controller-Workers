from abc import ABC, abstractmethod
from typing import Optional, Tuple, List

import socket
import struct

from common.command import CommandType, CommandParams, pack_command
from common.data import REGISTER_RESPONSE
from common.image import Image
from common import udp


class Client(ABC):

    def __init__(self, id: int):
        self._id = id

    @property
    def id(self) -> int:
        return self._id

    @abstractmethod
    def send_command(self, command: CommandType, params: Optional[CommandParams] = None):
        pass

    @abstractmethod
    def receive_image(self) -> Optional[Image]:
        pass


class Connection(ABC):

    @abstractmethod
    def do_discovery(self) -> List[Client]:
        pass

    @abstractmethod
    def broadcast(self, command: CommandType, params: Optional[CommandParams] = None):
        pass

    @abstractmethod
    def close(self):
        pass


class UdpClient(Client):

    def __init__(self, id: int, socket: socket.socket, address: Tuple):
        super().__init__(id)
        self._socket = socket
        self._address = address

    def send_command(self, command: CommandType, params: Optional[CommandParams] = None):
        command_data = pack_command(command, params)
        self._socket.sendto(command_data, self._address)

    def receive_image(self) -> Optional[Image]:
        return udp.receive_image(self._socket)


class UdpConnection(Connection):
    _BROADCAST_ADDRESS = '<broadcast>'
    _DISCOVERY_COMMAND = CommandType.REGISTER
    _DISCOVERY_RESPONSE = REGISTER_RESPONSE

    def __init__(self, skt: socket.socket, clients_port: int):
        self._socket = skt
        self._clients_port = clients_port
        self._client_id_generator = 0

    def do_discovery(self) -> List[Client]:
        # Send to all the clients that they should report their existence.
        self.broadcast(CommandType.REGISTER)

        clients = []
        # Collect responses from clients
        while True:
            try:
                client = self._discovery_once()
                clients.append(client)
            except socket.timeout as e:
                # If we receive a timeout it's because there are no more
                # clients and so we're finished with this.
                print('No more clients')
                break

        return clients

    def broadcast(self, command: CommandType, params: Optional[CommandParams] = None):
        command_data = pack_command(command, params)
        self._socket.sendto(command_data, (self._BROADCAST_ADDRESS, self._clients_port))

    def close(self):
        self._socket.close()

    def _discovery_once(self) -> Client:
        # Wait to receive info from a client.
        data, client = self._socket.recvfrom(len(self._DISCOVERY_RESPONSE))

        # Make and ID for the client
        self._client_id_generator += 1
        id = self._client_id_generator
        print('New client:', client, 'ID:', id)

        # Send the client a response with their id
        data = struct.pack('i', id)
        self._socket.sendto(data, client)
        # Return the client
        return UdpClient(id, self._socket, client)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return self

    @staticmethod
    def create(local_port: int, clients_port: int, timeout: float = None):
        skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Enable broadcasting mode
        skt.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        if timeout is not None:
            # Set the timeout for reading info, so that we get timeout exception.
            skt.settimeout(timeout)
        # Bind the socket to the address and port.
        skt.bind(('', local_port))

        return UdpConnection(skt, clients_port)

