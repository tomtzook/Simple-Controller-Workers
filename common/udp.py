from typing import Optional, Tuple

import socket
import struct
import io

from common.image import Image

MAX_UDP_SIZE = 64000
IMAGE_HEADER_FORMAT = 'iiii'  # client_id, image_id, index, has next


def send_no_image(socket: socket.socket, sender_id: int, dest_address: Tuple[str, int]):
    # If we don't have anymore images, then we send a response
    # indicating that by setting the picture id to -1.
    header = struct.pack(IMAGE_HEADER_FORMAT, sender_id, -1, 0, 0)
    socket.sendto(header, dest_address)


def send_image(socket: socket.socket, sender_id: int, dest_address: Tuple[str, int], image: Image):
    # Because UDP has a size limit, we must send the image in parts.
    # Each part of the image is sent with an header + data, where the header
    # contains information about the client and the image and the data is
    # part of the image.

    image_size = len(image)  # total image size
    header_size = struct.calcsize(IMAGE_HEADER_FORMAT)  # size of header
    # Maximum size of a part of image. Based on the size limitations of UDP
    # and the header size
    max_part_size = MAX_UDP_SIZE - header_size

    image_data = image.data

    # We will no run in a loop and send the image part by part until
    # we've sent everything.
    last_index = 0
    part_index = 0
    while image_size > 0:
        # The current data size (part size).
        # If the image still has more data then we can send at once,
        # we set the size to the maximum possible size.
        # If the image left has enough data to fit in one send, we set
        # the size to the data left.
        # We then update the remaining size of the image
        if image_size < max_part_size:
            current_size = image_size
        else:
            current_size = max_part_size

        image_size -= current_size

        # If the remaining size is less than 1, then we don't have more parts.
        if image_size <= 0:
            has_next = 0
        else:
            has_next = 1

        print('Sending part', part_index)

        # Build the header and data, and send.
        header = struct.pack(IMAGE_HEADER_FORMAT, sender_id, image.id, part_index, has_next)
        data = image_data[last_index:(last_index + current_size)]
        socket.sendto(header + data, dest_address)

        # Prepare for next run of the loop.
        last_index = last_index + current_size
        part_index += 1


def receive_image(socket: socket.socket) -> Optional[Image]:
    # Because of size limitations of UDP, we will expect the image in parts.
    # We will store the parts in image_parts (by order according to the header).
    image_parts = []
    header_size = struct.calcsize(IMAGE_HEADER_FORMAT)

    # We will run until the client tells us that there are no more parts.
    while True:
        # Receive data from the client.
        # The data is made up of header and image data.
        # We unpack the header information to understand more about the information we received.
        data, addr = socket.recvfrom(MAX_UDP_SIZE)
        header, data = data[:header_size], data[header_size:]
        sender_id, image_id, index, has_next = struct.unpack(IMAGE_HEADER_FORMAT, header)

        # If the image id is negative, then there is no image to read.
        if image_id < 0:
            return None

        print('Received part', index, 'Next?', has_next)

        # We need to place data in the image_parts list. This must be by order as specified by
        # index.
        if len(image_parts) <= index:
            image_parts.insert(index, data)
        else:
            image_parts[index] = data

        # If has_next is 0, then the client has no more parts to send.
        if has_next == 0:
            break

    # Combine all the parts of the image and return the it.
    image = io.BytesIO()
    for part in image_parts:
        image.write(part)

    return Image(image_id, image.getvalue())
