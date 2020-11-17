from typing import Optional

from common.command import Command
from common.image import Image
from master.client import Connection, Client
from master.storage import Storage


class Master(object):

    def __init__(self, connection: Connection, storage: Storage):
        self._connection = connection
        self._storage = storage
        self._clients = []

    def discover_clients(self):
        self._clients = self._connection.do_discovery()

    def take_picture(self):
        self._connection.broadcast(Command.TAKE_PICTURE)

    def collect_pictures(self):
        for client in self._clients:
            self._collect_pictures_from_client(client)

    def _collect_pictures_from_client(self, client: Client):
        print('Results from client:', client)
        while True:
            image = self._collect_one_picture(client)
            if image is None:
                break

            # Save the image so we can review later
            self._storage.store_image(client, image)

    def _collect_one_picture(self, client: Client) -> Optional[Image]:
        # Request the next image from the user.
        client.send_command(Command.SEND_NEXT_PICTURE)
        # Read the data from the client
        image = client.receive_image()
        if image is None:
            print('No more images from client')
            return None

        print('New result:', client.id, image.id)
        return image
