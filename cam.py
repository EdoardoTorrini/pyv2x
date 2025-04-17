from pyv2x.v2x_utils import ItsPduHeader


class CAM(ItsPduHeader):
    
    _required = [ "stationID" ]

    def __init__(self, **kwargs):

        if not all(elem in self._required for elem in kwargs.keys()):
            raise Exception(f"missing parameter for CAM frame, need: {self._required}")

        self.__dict__.update(kwargs)
        super().__init__(protocolVersion=2, messageID=2, stationID=self.stationID)

        