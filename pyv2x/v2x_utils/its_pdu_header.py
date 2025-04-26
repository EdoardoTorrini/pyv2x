

class ItsPduHeader:

    _header_req = [ "version", "message_id", "station_id" ]

    def __init__(self, **kwargs):

        if not all(req in kwargs.keys() for req in self._header_req):
            raise Exception("missing parameter for create ItsPduHeader")
        
        self.__dict__.update(kwargs)

