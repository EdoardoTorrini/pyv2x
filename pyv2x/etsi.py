from scapy.packet import Packet, Raw
from scapy.layers.l2 import SNAP, LLC
from scapy.layers.dot11 import Dot11, Dot11QoS, RadioTap
from scapy.compat import raw

from pyv2x.v2x_utils import GeoNetworking, BTPb
from pyv2x.v2x_cam import CAM

import os
import time
import asn1tools
from typeguard import typechecked


ETSI_DENM   = 1
ETSI_CAM    = 2

required_geo = [ "gn_addr_address", "latitude", "longitude", "speed", "heading" ]

@typechecked
class ETSI(object):

    header_file = "etsi_its_header.asn" 
    header_path = os.path.join(
        os.path.dirname( os.path.realpath(__file__) ),
        header_file
    )

    header = asn1tools.compile_files(header_path, 'uper') 

    @classmethod
    def get_message_id(cls, pkt: Packet) -> int:

        # SNAP and Raw are necessary to access to ETSI packages
        if not pkt.haslayer(SNAP) and not pkt.haslayer(Raw) and not pkt.haslayer(SNAP): return -1
        
        # if the SNAP code is not 0x8947 the packet not contain an GeoNetwork packet 
        if pkt[SNAP].code != 0x8947: return -1;
            
        geo = GeoNetworking(pkt[Raw].load)
        
        # for CAM and DENM the geo.common_next_header is equal to 2 (BTPb)
        if geo.common_next_header != 2: return -1
        return cls.header.decode('ItsPduHeader', bytes(BTPb(bytes(geo.payload)).payload)).get("messageID")

    @classmethod
    def get_cam_payload(cls, pkt: Packet, cam: asn1tools.compiler.Specification) -> dict:

        if cls.get_message_id(pkt) != ETSI_CAM:
            raise Exception("this is not a CAM packet")
        
        return cam.decode('CAM', bytes(BTPb(bytes(GeoNetworking(pkt[Raw].load).payload)).payload))

    @classmethod
    def geo(cls, **kwargs) -> GeoNetworking:
        
        if not all(req in kwargs.keys() for req in required_geo):
            raise Exception(f"missing parameter for create a GeoNetwork frame, need {required_geo}")

        param = { key: kwargs[key] for key in required_geo }
        return GeoNetworking(**param, timestamp=GeoNetworking.get_gn_timestamp())

    @classmethod
    def new_cam(cls, cam: asn1tools.compiler.Specification, **kwargs) -> Packet:
        
        geo, btpb = cls.geo(**kwargs), BTPb(destination_port=2001, info=0x5400)

        geo_raw, btpb_raw = raw(geo), raw(btpb)
        cam_raw = raw(cam.encode("CAM", CAM(**kwargs).get_dict()))

        dot11 = Dot11(subtype=8, type=2, proto=0, ID=0, addr1="ff:ff:ff:ff:ff:ff", addr2=kwargs.get("gn_addr_address"), addr3="ff:ff:ff:ff:ff:ff", SC=480)
        qos = Dot11QoS(A_MSDU_Present=0, Ack_Policy=1, EOSP=0, TID=3, TXOP=0)

        llc = LLC(dsap=0xaa, ssap=0xaa, ctrl=3)
        snap = SNAP(OUI=0, code=0x8947)

        mex = Raw(load=geo_raw+btpb_raw+cam_raw)
        radio = RadioTap(present=0x400000, timestamp=int(time.perf_counter()), ts_accuracy=0, ts_position=0, ts_flags=None)

        mex = radio / dot11 / qos / llc / snap / mex

        return mex