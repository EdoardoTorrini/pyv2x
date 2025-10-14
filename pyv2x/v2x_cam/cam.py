from pyv2x.v2x_utils import ItsPduHeader
from pyshark.packet.packet import Packet

from typeguard import typechecked


@typechecked
class CAM(ItsPduHeader):

    name = "CAM"

    _cam_req = ["station_id", "delta_time", "latitude", "longitude", "heading", "speed"]

    _alt_conf = {
        "0": "alt-000-01",
        "1": "alt-000-02",
        "2": "alt-000-05",
        "3": "alt-000-10",
        "4": "alt-000-20",
        "5": "alt-000-50",
        "6": "alt-001-00",
        "7": "alt-002-00",
        "8": "alt-005-00",
        "9": "alt-010-00",
        "10": "alt-unknown",
    }

    _curv_conf = {
        "0": "onePerMeter-0-00002",
        "1": "onePerMeter-0-0001",
        "2": "onePerMeter-0-0005",
        "3": "onePerMeter-0-001",
        "4": "onePerMeter-0-005",
        "5": "onePerMeter-0-01",
        "6": "onePerMeter-0-1",
        "7": "unavailable",
    }

    _drive_direction = {"0": "forward", "1": "backward"}

    def __init__(self, **kwargs):

        pkt = kwargs.get("flat", None)
        if pkt is not None and not hasattr(pkt, "its"):
            raise Exception("flat pkt - pyshark - does not have its layer")

        kwargs = {
            "station_id": self._get(pkt, "its", "stationId", kwargs.get("station_id")),
            "delta_time": self._get(pkt, "its", "cam_generationdeltatime", kwargs.get("delta_time")),
            "latitude": self._get(pkt, "its", "latitude", kwargs.get("latitude")),
            "longitude": self._get(pkt, "its", "longitude", kwargs.get("longitude")),
            "heading": self._get(pkt, "its", "headingValue", kwargs.get("heading")),
            "speed": self._get(pkt, "its", "speedValue", kwargs.get("speed")),
            "station_type": self._get(pkt, "its", "stationType", 5),
            "semi_major_conf": self._get(pkt, "its", "semiMajorAxisLength", 282),
            "semi_minor_conf": self._get(pkt, "its", "semiMinorAxisLength", 280),
            "semi_major_orientation": self._get(pkt, "its", "semiMajorAxisOrientation", 1138),
            "altitude_value": self._get(pkt, "its", "altitudeValue", 10),
            "altitude_confidence": self._enum(pkt, "its", "altitudeConfidence", self._alt_conf, "alt-000-01"),
            "heading_confidence": self._get(pkt, "its", "headingConfidence", 1),
            "speed_confidence": self._get(pkt, "its", "speedConfidence", 1),
            "drive_direction": self._enum(pkt, "its", "cam_drivedirection", self._drive_direction, "forward"),
            "vehicle_length": self._get(pkt, "its", "vehicleLengthValue", 42),
            "vehicle_length_conf": "trailerPresenceIsUnknown",
            "vehicle_width": self._get(pkt, "its", "cam_vehiclewidth", 18),
            "longitudinal_accel": self._get(pkt, "its", "value", -2),
            "longitudinal_accel_conf": self._get(pkt, "its", "confidence", 102),
            "curvature_value": self._get(pkt, "its", "curvatureValue", 386),
            "curvature_conf": self._enum(pkt, "its", "curvatureConfidence", self._curv_conf, "onePerMeter-0-01"),
            "yaw_rate_value": self._get(pkt, "its", "yawRateValue", 2354),
            "yaw_rate_conf": "unavailable",
            "acceleration_control": self._bitmask_to_bytes(self._get(pkt, "its", "cam_accelerationcontrol", 0, str)),
            "steering_angle_value": self._get(pkt, "its", "steeringWheelAngleValue", 57),
            "steering_angle_conf": self._get(pkt, "its", "steeringWheelAngleConfidence", 1),
            # TODO: understand why in the pyshark pkt there is no difference between longitudinalAccelerationValue and lateralAccelerationValue
            "lateral_accel_value": 43,
            "lateral_accel_conf": self._get(pkt, "its", "confidence", 102),
            "gn_addr_address": self._get(pkt, "gnw", "gn_addr_address", "ff:ff:ff:ff:ff:ff:ff:ff", str)
        }
        
        if not all(req in kwargs for req in self._cam_req):
            raise Exception(f"Missing parameter for CAM frame, need: {self._cam_req}")

        self.__dict__.update(kwargs)
        super().__init__(version=2, message_id=2, station_id=self.station_id)
    
    def __iter__(self):
        return iter(self.__dict__.items())

    def get_dict(self):
        return {
            "header": {
                "protocolVersion": self.version,
                "messageID": self.message_id,
                "stationID": self.station_id,
            },
            "cam": {
                "generationDeltaTime": self.delta_time,
                "camParameters": {
                    "basicContainer": {
                        "stationType": self.station_type,
                        "referencePosition": {
                            "latitude": self.latitude,
                            "longitude": self.longitude,
                            "positionConfidenceEllipse": {
                                "semiMajorConfidence": self.semi_major_conf,
                                "semiMinorConfidence": self.semi_minor_conf,
                                "semiMajorOrientation": self.semi_major_orientation,
                            },
                            "altitude": {
                                "altitudeValue": self.altitude_value,
                                "altitudeConfidence": self.altitude_confidence,
                            },
                        },
                    },
                    "highFrequencyContainer": (
                        "basicVehicleContainerHighFrequency",
                        {
                            "heading": {
                                "headingValue": self.heading,
                                "headingConfidence": self.heading_confidence,
                            },
                            "speed": {
                                "speedValue": self.speed,
                                "speedConfidence": self.speed_confidence,
                            },
                            "driveDirection": self.drive_direction,
                            "vehicleLength": {
                                "vehicleLengthValue": self.vehicle_length,
                                "vehicleLengthConfidenceIndication": self.vehicle_length_conf,
                            },
                            "vehicleWidth": self.vehicle_width,
                            "longitudinalAcceleration": {
                                "longitudinalAccelerationValue": self.longitudinal_accel,
                                "longitudinalAccelerationConfidence": self.longitudinal_accel_conf,
                            },
                            "curvature": {
                                "curvatureValue": self.curvature_value,
                                "curvatureConfidence": self.curvature_conf,
                            },
                            "curvatureCalculationMode": "yawRateUsed",
                            "yawRate": {
                                "yawRateValue": self.yaw_rate_value,
                                "yawRateConfidence": self.yaw_rate_conf,
                            },
                            "accelerationControl": self.acceleration_control,
                            "steeringWheelAngle": {
                                "steeringWheelAngleValue": self.steering_angle_value,
                                "steeringWheelAngleConfidence": self.steering_angle_conf,
                            },
                            "lateralAcceleration": {
                                "lateralAccelerationValue": self.lateral_accel_value,
                                "lateralAccelerationConfidence": self.lateral_accel_conf,
                            },
                        },
                    ),
                },
            },
        }


