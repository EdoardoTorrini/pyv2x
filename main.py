from pyv2x import ETSI, V2xTMsg
from pyv2x.v2x_msg import V2xMsg
from pyv2x.v2x_utils import V2xAsnP, GeoNetworking
from pyv2x.v2x_network import V2xNetwork

from datetime import datetime


cfiles = ["./asn/cam/CAM-PDU-Descriptions.asn", "./asn/cam/cdd/ITS-Container.asn"]
dfiles = ["./asn/denm/DENM-PDU-Descriptions.asn", "./asn/denm/cdd/ITS-Container.asn"]

CAM =  V2xAsnP.new("CAM", cfiles).create_class()
DENM = V2xAsnP.new("DENM", dfiles).create_class()

iface = "hwsim0"
net = V2xNetwork(iface, [CAM, DENM], enable_listener=False) 

msg = CAM(
    protocolVersion = 2,
    messageID = 2,
    stationID = 12121,
    generationDeltaTime = GeoNetworking.get_gn_timestamp(),
    stationType = 15,
    latitude = 446558300,
    longitude = 109275000,
    semiMajorConfidence = 282,
    semiMinorConfidence = 278,
    semiMajorOrientation = 616,
    altitudeValue = 9650,
    altitudeConfidence = "alt-020-00",
    headingValue = 1235,
    headingConfidence = 6,
    speedValue = 1223,
    speedConfidence = 2,
    driveDirection = "forward",
    vehicleLengthValue = 42,
    vehicleLengthConfidenceIndication = "trailerPresenceIsUnknown",
    vehicleWidth = 18,
    longitudinalAccelerationValue = -1,
    longitudinalAccelerationConfidence = 102,
    curvatureValue = 0,
    curvatureConfidence = "onePerMeter-0-01",
    curvatureCalculationMode = "yawRateUsed",
    yawRateValue = 1,
    yawRateConfidence = "unavailable",
)

net.send_msg( ETSI.format_msg(msg, gn_addr_address="3E:B5:93:C7:D8:57") )

msg = DENM(
    protocolVersion=2,
    messageID=1,
    stationID=12120,
    originatingStationID=12120,
    sequenceNumber=1,
    detectionTime=GeoNetworking.get_timestamp(),
    referenceTime=GeoNetworking.get_timestamp(),
    latitude=446558300,
    longitude=109275000,
    semiMajorConfidence=282,
    semiMinorConfidence=278,
    semiMajorOrientation=616,    
    altitudeValue=9650,
    altitudeConfidence="alt-020-00",
    validityDuration=1,
    stationType=15,
    situation_informationQuality=4,
    situation_eventType_causeCode=1,
    situation_eventType_subCauseCode=0,
)

net.send_msg( ETSI.format_msg(msg, gn_addr_address="3E:B5:93:C7:D8:57") )

import pyshark
from scapy.all import *

pcap_path = "./out.pcap"
for pkt in pyshark.FileCapture(input_file=pcap_path, use_json=True, include_raw=True, display_filter="its"):
# for pkt in rdpcap(pcap_path):
    
    message_id = ETSI.get_message_id(pkt)
    
    match message_id:

        case V2xTMsg.DENM: 
            msg = DENM(pkt=pkt)
            print(f"DENM msg: {msg}")
            net.send_msg( ETSI.format_msg( msg, gn_addr_address="E3:B5:93:C7:D8:57" ) )

        case V2xTMsg.CAM:
            msg = CAM(pkt=pkt)
            print(f"CAM msg: {msg}")
            net.send_msg( ETSI.format_msg( msg, gn_addr_address="E3:B5:93:C7:D8:57" ) )
