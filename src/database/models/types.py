from enum import Enum
from os import times
from typing import TypedDict


class LogType(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class Log(TypedDict):
    timestamp: str
    message: str
    type: str


class Location(TypedDict):
    city: str
    longitude_latitude: str
