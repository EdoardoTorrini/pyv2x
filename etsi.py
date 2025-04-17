from scapy.packet import Packet, Raw
from scapy.layers.l2 import SNAP

from v2t_utils import GeoNetworking, BTPb

import os
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
        if not pkt.haslayer(SNAP) and not pkt.haslayer(Raw): return -1
        
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
        
        if not all(elem in required_geo for elem in kwargs.keys()):
            raise Exception(f"missing parameter for create a GeoNetwork frame, need {required_geo}")

        return GeoNetworking(**kwargs, timestamp=GeoNetworking.get_gn_timestamp)

    @classmethod
    def new_cam(cls, cam: asn1tools.compiler.Specification, **kwargs) -> Packet:
        
        geo, btpb = cls.geo(**kwargs), BTPb(destination_port=2001, info=0x5400)


        return cls.geo(**kwargs)