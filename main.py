from asn1parser import *

from pyv2x import ETSI, V2xTMsg
from pyv2x.v2x_network import V2xNetwork

cfiles = ["./asn/cam/CAM-PDU-Descriptions.asn", "./asn/cam/cdd/ITS-Container.asn"]
dfiles = ["./asn/denm/DENM-PDU-Descriptions.asn", "./asn/denm/cdd/ITS-Container.asn"]

CAM =  V2xAsnP.new("CAM", cfiles).create_class()
DENM = V2xAsnP.new("DENM", dfiles).create_class()

# prova = CAM(protocolVersion=2, messageID=2, stationID=4316, stationType=15, generationDeltaTime=10000, latitude=446560626, longitude=109214040, altitudeValue=9650, speedValue=2777)
# print("attr: ", dict(prova))
# print("as_dict: ", prova.as_dict())
# print("enc: ", prova.encode())

# iface = "hwsim0"
# net = V2xNetwork(iface, CAM.get_spec(), DENM.get_spec()) 

import pyshark
from scapy.all import *

for pkt in pyshark.FileCapture(input_file="./out.pcap", use_json=True, include_raw=True):
# for pkt in rdpcap('./out.pcap'):
    
    message_id = ETSI.get_message_id(pkt)
    
    match message_id:

        case V2xTMsg.ETSI_DENM: 
            msg = DENM(pkt=pkt)
            print(f"DENM msg: {msg}")

        case V2xTMsg.ETSI_CAM:
            msg = CAM(pkt=pkt)
            print(f"CAM msg: {msg}")
