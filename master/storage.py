from abc import ABC, abstractmethod
from pathlib import Path

from common.times import create_datetime_path
from common.image import Image
from master.client import Client


class Storage(ABC):

    @abstractmethod
    def store_image(self, client: Client, image: Image):
        pass


class BasicFileSystemStorage(Storage):

    def __init__(self, parent_path: Path, use_datetime: bool = False):
        if use_datetime:
            self._parent = create_datetime_path(parent_path)
        else:
            self._parent = parent_path

        if not self._parent.exists():
            self._parent.mkdir(parents=True)

    def store_image(self, client: Client, image: Image):
        client_dir = self._parent / str(client.id)
        if not client_dir.exists():
            client_dir.mkdir()

        image_path = client_dir / ('{}.{}'.format(str(image.id), image.extension))
        with image_path.open(mode='wb') as f:
            f.write(image.data)
