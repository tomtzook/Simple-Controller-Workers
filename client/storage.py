from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from common.times import create_datetime_path
from common.image import Image


class Storage(ABC):

    @abstractmethod
    def store_image(self, image: Image):
        pass

    @abstractmethod
    def retrieve_next_image(self) -> Optional[Image]:
        pass


class BasicFileSystemStorage(Storage):

    def __init__(self, parent_path: Path, use_datetime: bool = False):
        if use_datetime:
            self._parent = create_datetime_path(parent_path)
        else:
            self._parent = parent_path

        if not self._parent.exists():
            self._parent.mkdir(parents=True)

        self._stored_images = []

    def store_image(self, image: Image):
        # We will save the image in a local path
        image_path = self._parent / '{}.{}'.format(str(image.id), image.extension)
        with image_path.open(mode='wb') as f:
            f.write(image.data)

        # Save the path of the image to a list so we may recall it later.
        # Easier than querying the file system
        self._stored_images.append((image.id, image_path))

    def retrieve_next_image(self) -> Optional[Image]:
        # If we don't have anymore images
        if len(self._stored_images) == 0:
            return None

        # We take one path from the list of images and remove it
        # from the list.
        image_id, image_path = self._stored_images.pop()

        # Read the image from the file and return it.
        with image_path.open(mode='rb') as f:
            image = f.read()
            return Image(image_id, image)
