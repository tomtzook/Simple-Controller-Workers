from abc import ABC, abstractmethod
import enum
import struct


from typing import Optional, Tuple

# type + parameters
MAX_COMMAND_SIZE = 1024
# All command values must be of size 6
COMMAND_TYPE_SIZE = 6


class CommandParams(ABC):

    @abstractmethod
    def pack(self) -> bytes:
        pass

    @abstractmethod
    def unpack(self, data: bytes):
        pass


class TakePictureParams(CommandParams):

    def __init__(self, picture_id: int = -1):
        self._picture_id = picture_id

    @property
    def picture_id(self) -> int:
        return self._picture_id

    def pack(self) -> bytes:
        return struct.pack('i', self._picture_id)

    def unpack(self, data: bytes):
        self._picture_id, = struct.unpack('i', data)


class CommandType(enum.Enum):
    REGISTER = (b'regist', None)
    TAKE_PICTURE = (b'takpic', TakePictureParams)
    SEND_NEXT_PICTURE = (b'senimg', None)

    @staticmethod
    def from_header(header: bytes):
        for command_type in CommandType:
            if header == command_type.value[0]:
                return command_type

        raise ValueError('unknown command: ' + str(header))


def pack_command(command: CommandType, params: Optional[CommandParams]) -> bytes:
    type_header, params_class = command.value
    if params is None:
        if params_class is not None:
            raise ValueError('expected parameters of type: ' + params_class)
        return type_header
    else:
        if params_class != type(params):
            raise ValueError('expected parameters of type: ' + params_class)
        return type_header + params.pack()


def unpack_command(data: bytes) -> Tuple[CommandType, Optional[CommandParams]]:
    type_header = data[:COMMAND_TYPE_SIZE]
    command_type = CommandType.from_header(type_header)
    params_class = command_type.value[1]
    if params_class is None:
        params = None
    else:
        params_data = data[COMMAND_TYPE_SIZE:]
        params = params_class()
        params.unpack(params_data)

    return command_type, params
