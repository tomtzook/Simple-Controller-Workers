from pathlib import Path

import time

from common.command import Command
from master.client import UdpConnection
from master.master import Master
from master.storage import BasicFileSystemStorage

from settings import *

WAIT_BETWEEN_PICS_SEC = 10  # seconds
RUN_EXPERIMENT_TIMES = 2  # 5 = 50 seconds, 5 images

SERVER_TIMEOUT = 1  # seconds
STORAGE_PARENT = Path('results')


def main():
    storage = BasicFileSystemStorage(STORAGE_PARENT, use_datetime=True)
    with UdpConnection.create(SERVER_PORT, CLIENT_PORT, timeout=SERVER_TIMEOUT) as connection:
        master = Master(connection, storage)

        # Let's familiarize ourselves with all the clients:
        print('Registering clients')
        master.discover_clients()

        # Run several times (how many times we want to take pictures).
        for i in range(RUN_EXPERIMENT_TIMES):
            print('Taking picture')
            # Notify all clients to take a picture
            connection.broadcast(Command.TAKE_PICTURE)
            # Wait until next time to take a picture
            time.sleep(WAIT_BETWEEN_PICS_SEC)

        # Collect results:
        print('Collecting results')
        master.collect_pictures()

        print('Done')


if __name__ == '__main__':
    main()
