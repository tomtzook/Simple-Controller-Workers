import enum


# All command values must be of size 6
COMMAND_SIZE = 6


class Command(enum.Enum):
    REGISTER = b'regist'
    TAKE_PICTURE = b'takpic'
    SEND_NEXT_PICTURE = b'senimg'
