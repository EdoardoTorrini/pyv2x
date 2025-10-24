from pyv2x import ETSI, V2xTMsg
from pyv2x.v2x_msg import V2xMsg
from pyv2x.v2x_utils import V2xAsnP
from pyv2x.v2x_network import V2xNetwork


cfiles = ["./asn/cam/CAM-PDU-Descriptions.asn", "./asn/cam/cdd/ITS-Container.asn"]
dfiles = ["./asn/denm/DENM-PDU-Descriptions.asn", "./asn/denm/cdd/ITS-Container.asn"]

CAM =  V2xAsnP.new("CAM", cfiles).create_class()
DENM = V2xAsnP.new("DENM", dfiles).create_class()

# msg = CAM(
#     protocolVersion = 2,
#     messageID = 2,
#     stationID = 12121,
#     generationDeltaTime = 10000,
#     stationType = 15,
#     latitude = 446558300,
#     longitude = 109275000,
#     semiMajorConfidence = 282,
#     semiMinorConfidence = 278,
#     semiMajorOrientation = 616,
#     altitudeValue = 9650,
#     altitudeConfidence = "alt-020-00",
#     headingValue = 1235,
#     headingConfidence = 6,
#     speedValue = 2777,
#     speedConfidence = 4,
#     driveDirection = "forward",
#     vehicleLengthValue = 42,
#     vehicleLengthConfidenceIndication = "trailerPresenceIsUnknown",
#     vehicleWidth = 18,
#     longitudinalAccelerationValue = -1,
#     longitudinalAccelerationConfidence = 102,
#     curvatureValue = 0,
#     curvatureConfidence = "onePerMeter-0-01",
#     curvatureCalculationMode = "yawRateUsed",
#     yawRateValue = 1,
#     yawRateConfidence = "unavailable",
#     accelerationControl = (b'@', 7),
#     lanePosition = 0,
#     steeringWheelAngleValue = 0,
#     steeringWheelAngleConfidence = 1,
#     lateralAccelerationValue = 1,
#     lateralAccelerationConfidence = 102
# )

# print("attr: ", dict(prova))
# print("as_dict: ", prova.as_dict())
# print("enc: ", prova.encode())

# iface = "hwsim0"
# net = V2xNetwork(iface, [CAM, DENM]) 

import pyshark
from scapy.all import *

pcap_path = "./out.pcap"
for pkt in pyshark.FileCapture(input_file=pcap_path, use_json=True, include_raw=True, display_filter="its"):
# for pkt in rdpcap('./out.pcap'):
    
    message_id = ETSI.get_message_id(pkt)
    
    match message_id:

        case V2xTMsg.DENM: 
            msg = DENM(pkt=pkt)
            print(f"DENM msg: {msg}")

        case V2xTMsg.CAM:
            msg = CAM(pkt=pkt)
            print(f"CAM msg: {msg}")
