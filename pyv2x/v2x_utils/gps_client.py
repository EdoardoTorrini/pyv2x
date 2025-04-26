import serial

from os import path
from pynmeagps import NMEAReader

import json


class GPRMC:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class GPSclient:

    _file = "/dev/ttyACM0"
    _baudrate = 9600

    @classmethod
    def new(cls, file: str, baud: int) -> "GPSclient":
        if not path.exists(file):
            raise Exception(f"file {file} not found")
        
        cls._baudrate, cls._file = baud, file
        return cls()

    @classmethod
    def get_data(cls):
        with serial.Serial(cls._file, cls._baudrate, timeout=1) as file:
            raw_data, parsed_data = NMEAReader(file).read()
            if parsed_data is None:
                raise Exception(f"wrong parsing: {raw_data}")
        
        match parsed_data.__dict__["_msgID"]:
            case "RMC":
                return GPRMC(
                    time=parsed_data.time.strftime("%H%M%S"), status=parsed_data.status, latitude=parsed_data.lat,
                    NS=parsed_data.NS, longitude=parsed_data.lon, EW=parsed_data.EW, speedValue=parsed_data.spd,
                    headingValue=parsed_data.cog, date=parsed_data.date, mv=parsed_data.mv, mode=parsed_data.posMode
                )
            case _:
                return None