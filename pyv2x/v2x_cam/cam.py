from pyv2x.v2x_utils import ItsPduHeader

from typeguard import typechecked

@typechecked
class CAM(ItsPduHeader):
    
    _cam_req = [ "station_id", "delta_time", "latitude", "longitude", "heading", "speed" ]

    def __init__(self, **kwargs) -> None:

        if not all(req in kwargs.keys() for req in self._cam_req):
            raise Exception(f"missing parameter for CAM frame, need: {self._cam_req}")
        self.__dict__.update(kwargs)

        super().__init__(version=2, message_id=2, station_id=self.station_id)
    
    def get_dict(self):
        # TODO: remove all static parameters
        return {
            "header": {"protocolVersion": self.version, "messageID": self.message_id, "stationID": self.station_id},
            "cam": {
                "generationDeltaTime": self.delta_time, 
                "camParameters": {
                    "basicContainer": {
                        "stationType": 5,
                        "referencePosition": {
                            "latitude": self.latitude, "longitude": self.longitude,
                            "positionConfidenceEllipse": {
                                "semiMajorConfidence": 282,
                                "semiMinorConfidence": 280,
                                "semiMajorOrientation": 1138
                            },
                            "altitude": {
                                "altitudeValue": 10, 
                                "altitudeConfidence": "alt-000-01"
                            }
                        }
                    },
                    "highFrequencyContainer": ("basicVehicleContainerHighFrequency",
                    {
                        "heading": {
                            "headingValue": self.heading, 
                            "headingConfidence": 1
                        },
                        "speed": {
                            "speedValue": self.speed, 
                            "speedConfidence": 1
                        },
                        "driveDirection": "forward",
                        "vehicleLength": {
                            "vehicleLengthValue": 42, 
                            "vehicleLengthConfidenceIndication": "trailerPresenceIsUnknown"
                        },
                        "vehicleWidth": 18,
                        "longitudinalAcceleration": {
                            "longitudinalAccelerationValue": -2,
                            "longitudinalAccelerationConfidence": 102
                        },
                        "curvature": {
                            "curvatureValue": 386, 
                            "curvatureConfidence": "onePerMeter-0-01"
                        }, 
                        "curvatureCalculationMode": "yawRateUsed", 
                        "yawRate": {
                            "yawRateValue": 2354, 
                            "yawRateConfidence": "unavailable"
                        }, 
                        "accelerationControl": (b"@", 7),
                        "steeringWheelAngle": {
                            "steeringWheelAngleValue": 57, 
                            "steeringWheelAngleConfidence": 1
                        }, 
                        "lateralAcceleration": {
                            "lateralAccelerationValue": 43, 
                            "lateralAccelerationConfidence": 102
                        }
                    })
                }
            }
        }