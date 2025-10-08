from pyv2x.v2x_utils import ItsPduHeader

from typeguard import typechecked

@typechecked
class DENM(ItsPduHeader):

    name = "DENM"

    _denm_req = [ "station_id", "delta_time", "latitude", "longitude", "distance", "traffic_direction" ]
    _rel_distance = [ "lessThan50m", "lessThan100m", "lessThan200m", "lessThan500m", "lessThan1000m", "lessThan5km", "lessThan10km", "over10km" ]
    _rel_traffic_direction = [ "allTrafficDirections", "upstreamTraffic", "downstreamTraffic", "oppositeTraffic" ]

    def __init__(self, **kwargs) -> None:
        
        if not all(req in kwargs.keys() for req in self._denm_req):
            raise Exception(f"missing parameter for DENM frame, need: {self._denm_req}")
        self.__dict__.update(kwargs)

        if self.distance not in self._rel_distance:
            raise Exception(f"distance parameter must be in: {self._rel_distance}")
        
        if self.traffic_direction not in self._rel_traffic_direction:
            raise Exception(f"traffic direction parameter must be in: {self._rel_traffic_direction}")

        super().__init__(version=2, message_id=1, station_id=self.station_id)

    def get_dict(self):
        # TODO: remove all static parameters
        return {
            'header': {'protocolVersion': self.version, 'messageId': self.message_id, 'stationId': self.station_id}, 
            'denm': {
                'management': {
                    'actionID': {
                        'originatingStationId': 999, 
                        'sequenceNumber': 101
                    }, 
                    'detectionTime': self.delta_time, 
                    'referenceTime': self.delta_time,
                    'eventPosition': {
                        'latitude': self.latitude, 'longitude': self.longitude, 
                        'positionConfidenceEllipse': {
                            'semiMajorConfidence': 100,
                            'semiMinorConfidence': 100, 
                            'semiMajorOrientation': 0
                        }, 
                        'altitude': {
                            'altitudeValue': 10, 
                            'altitudeConfidence': 'alt-000-01'
                        }
                    },
                    'relevanceDistance': self.distance, 
                    'relevanceTrafficDirection': self.traffic_direction, 
                    'validityDuration': 59, 
                    'stationType': 15
                }, 
                'situation': {
                    'informationQuality': 6, 
                    'eventType': {
                        'causeCode': 3, 
                        'subCauseCode': 0
                    }
                },
            }
        }
