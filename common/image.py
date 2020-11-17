

class Image(object):

    def __init__(self, id: int, data: bytes):
        self._id = id
        self._data = data

    @property
    def id(self) -> int:
        return self._id

    @property
    def data(self) -> bytes:
        return self._data

    @property
    def extension(self):
        return 'jpg'

    def __len__(self):
        return len(self._data)
