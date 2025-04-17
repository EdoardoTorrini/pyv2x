

class ItsPduHeader:

    _required = [ "protocolVersion", "messageID", "stationID" ]

    def __init__(self, **kwargs):

        if not all(elem in self._required for elem in kwargs):
            raise Exception("missing parameter for create ItsPduHeader")
        
        self.__dict__.update(kwargs)

