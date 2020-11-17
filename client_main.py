from pathlib import Path

from client.camera import StubCamera
from client.client import Client
from client.connection import UdpConnection
from client.storage import BasicFileSystemStorage

from settings import *

STORAGE_PARENT = Path('client_results')
SERVER_ADDRESS = ('localhost', SERVER_PORT)


def main():
    storage = BasicFileSystemStorage(STORAGE_PARENT, use_datetime=True)
    with StubCamera() as camera, \
            UdpConnection.create(CLIENT_PORT, SERVER_ADDRESS) as conn:
        client = Client(conn, storage, camera)

        print('Starting')
        while True:
            client.handle_next_command()


if __name__ == '__main__':
    main()
