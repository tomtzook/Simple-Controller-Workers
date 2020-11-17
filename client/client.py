from client.camera import Camera
from client.connection import Connection
from client.storage import Storage
from common.command import Command
from common.image import Image


class Client(object):

    def __init__(self, connection: Connection, storage: Storage, camera: Camera):
        self._connection = connection
        self._storage = storage
        self._camera = camera
        self._command_handlers = {
            Command.REGISTER: self._register_to_server,
            Command.TAKE_PICTURE: self._take_picture,
            Command.SEND_NEXT_PICTURE: self._send_next_picture
        }

        self._id = -1
        self._next_image_id = 0

    def handle_next_command(self):
        command = self._connection.wait_for_command()
        handler = self._command_handlers[command]
        handler()

    def _register_to_server(self):
        # If the command is to register:
        print('Register request')

        # send the server a response
        new_id = self._connection.send_register()
        print('New ID:', new_id)
        self._id = new_id

    def _take_picture(self):
        # If the command is to take a picture:
        print('Take picture request')

        # Increment the picture id so it will represent the new image.
        self._next_image_id += 1
        image_id = self._next_image_id

        # Take picture
        data = self._camera.take_picture()
        image = Image(image_id, data)

        # We will save the image.
        self._storage.store_image(image)

    def _send_next_picture(self):
        # If the command is to send an image:
        print('Send image request')

        next_picture = self._storage.retrieve_next_image()
        if next_picture is None:
            print('No more images')
            self._connection.send_no_image(self._id)
        else:
            self._connection.send_image(self._id, next_picture)
            print('Image sent')
