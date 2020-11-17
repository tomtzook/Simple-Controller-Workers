from abc import ABC, abstractmethod

import random


class Camera(ABC):

    @abstractmethod
    def take_picture(self) -> bytes:
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self


class StubCamera(Camera):

    def take_picture(self) -> bytes:
        images = [
            'menu-1.png',
            'menu3.1.png',
            'menu22.3.png'
        ]
        parent = '/home/tomtzook/Pictures/'

        image = random.choice(images)
        with open(parent + image, mode='rb') as f:
            return f.read()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self
