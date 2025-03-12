from enum import Enum
from typing import TypedDict


class LogType(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class Log(TypedDict):
    message: str
    type: LogType


class Location(TypedDict):
    city: str
    longitude_latitude: str
