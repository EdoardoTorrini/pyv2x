from pyv2x.v2x_utils import ItsPduHeader
from pyshark.packet.packet import Packet

from typeguard import typechecked


@typechecked
class DENM(ItsPduHeader):

    name = "DENM"
    _denm_req = [ "station_id", "detection_time", "latitude", "longitude", "relevance_traffic_direction", "cause_code" ]
    
    # TODO: fare una classe con queste informazioni
    _cause_code = {
        "0":    "trafficCondition",
        "1":    "accident",
        "2":    "roadworks",
        "3":    "adverseWeatherCondition-Adhesion",
        "4":    "hazardousLocation-SurfaceCondition",
        "5":    "hazardousLocation-ObstacleOnTheRoad",
        "6":    "hazardousLocation-AnimalOnTheRoad",
        "7":    "humanPresenceOnTheRoad",
        "8":    "wrongWayDriving",
        "9":    "rescueAndRecoveryWorkInProgress",
        "10":   "adverseWeatherCondition-ExtremeWeather",
        "11":   "adverseWeatherCondition-Visibility",
        "12":   "adverseWeatherCondition-Precipitation",
        "13":   "slowVehicle",
        "14":   "dangerousEndOfQueue",
        "15":   "vehicleBreakdown",
        "16":   "postCrash",
        "17":   "humanProblem",
        "18":   "stationaryVehicle",
        "19":   "emergencyVehicleApproaching",
        "20":   "hazardousLocation-DangerousCurve",
        "21":   "collisionRisk",
        "22":   "signalViolation",
        "23":   "dangerousSituation",
    }

    # TODO: altra classe
    _info_quality = {
        "0": "unavailable",
        "1": "lowest",
        "2": "veryLow",
        "3": "low",
        "4": "medium",
        "5": "high",
        "6": "veryHigh",
        "7": "highest",
    }

    _event_pos_confidence = {
        "0": "unavailable",
        "1": "low",
        "2": "medium",
        "3": "high",
    }

    _relevance_distance = {
        "0": "lessThan50m",
        "1": "lessThan100m",
        "2": "lessThan200m",
        "3": "lessThan500m",
        "4": "lessThan1000m",
        "5": "lessThan5km",
        "6": "lessThan10km",
        "7": "over10km",
        "8": "unavailable",
    }

    _relevance_traffic_direction = {
        "0": "upstreamTraffic",
        "1": "downstreamTraffic",
        "2": "oppositeTraffic",
        "3": "allTrafficDirections",
        "4": "unavailable",
    }

    def __init__(self, **kwargs) -> None:
        
        if not all(req in kwargs.keys() for req in self._denm_req):
            raise Exception(f"missing parameter for DENM frame, need: {self._denm_req}")
        
        self.__dict__.update(kwargs)
        


        super().__init__(version=2, message_id=1, station_id=self.station_id)
    
    def get_dict(self):
        return {
            'header': {
                'protocolVersion': self.protocol_version,
                'messageID': self.message_id,
                'stationID': self.station_id
            },
            'denm': {
                'management': {
                    'actionID': {
                        'originatingStationID': self.originating_station_id,
                        'sequenceNumber': self.sequence_number
                    },
                    'detectionTime': self.detection_time,
                    'referenceTime': self.reference_time,
                    'eventPosition': {
                        'latitude': self.latitude,
                        'longitude': self.longitude,
                        'positionConfidenceEllipse': {
                            'semiMajorConfidence': self.semi_major_confidence,
                            'semiMinorConfidence': self.semi_minor_confidence,
                            'semiMajorOrientation': self.semi_major_orientation
                        },
                        'altitude': {
                            'altitudeValue': self.altitude_value,
                            'altitudeConfidence': self.altitude_confidence
                        }
                    },
                    'relevanceDistance': self.relevance_distance,
                    'relevanceTrafficDirection': self.relevance_traffic_direction,
                    'validityDuration': self.validity_duration,
                    'stationType': self.station_type
                },
                'situation': {
                    'informationQuality': self.information_quality,
                    'eventType': {
                        'causeCode': self.cause_code,
                        'subCauseCode': self.sub_cause_code
                    }
                }
            }
        }
 
