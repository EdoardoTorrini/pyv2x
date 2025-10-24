from pyshark.packet.packet import Packet


class ItsPduHeader:

    _header_req = [ "version", "message_id", "station_id" ]

    @staticmethod
    def _get(d: Packet | None, sub: str, key: str, default: int | str | None = 0, cast: type = int):
        try:
            query = getattr(d, sub, None)
            return cast(getattr(query, key, default))
        except (KeyError, ValueError, TypeError, AttributeError):
            return cast(default)

    @staticmethod
    def _enum(d: Packet | None, sub: str, key: str, mapping: dict, default: int | str | None):
        try:
            query = getattr(d, sub, None)
            val = mapping.get(str(query.get(key)), default)
        except (KeyError, ValueError, TypeError, AttributeError):
            return default

    @staticmethod
    def _bitmask_to_bytes(value: str) -> tuple:
        try:
            intval = int(value)
            return (intval.to_bytes(1, "big"), 8)
        except Exception:
            return (b"\x00", 8)

    def __init__(self, **kwargs):

        if not all(req in kwargs.keys() for req in self._header_req):
            raise Exception("missing parameter for create ItsPduHeader")
        
        self.__dict__.update(kwargs)

