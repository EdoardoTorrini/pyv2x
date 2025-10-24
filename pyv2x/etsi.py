from scapy.packet import Packet, Raw
from scapy.layers.l2 import SNAP, LLC, Ether
from scapy.layers.dot11 import Dot11, Dot11QoS, RadioTap
from scapy.compat import raw

from pyshark.packet import packet

from pyv2x.v2x_utils import GeoNetworking, BTPb
from pyv2x.v2x_msg import V2xMsg

import os, time, asn1tools
from typeguard import typechecked


class IterMeta(type):

    def __iter__(cls):
        for k, v in cls.__dict__.items():
            if not k.startswith('_') and not callable(v):
                yield k, v

    def __len__(cls):
        return sum(1 for k in cls.__dict__.keys() 
                   if not k.startswith('_') and not callable(cls.__dict__[k]))

    def get(self, key, default=None):
        return self.__dict__.get(key, default)

# TODO: make this class dynamic using the parser
class V2xTMsg(metaclass=IterMeta):
    DENM = 1
    CAM = 2

required_geo = [ "gn_addr_address", "latitude", "longitude", "speed", "heading", "payload_lenght" ]

@typechecked
class ETSI(object):

    header_file = "etsi_its_header.asn" 
    header_path = os.path.join(
        os.path.dirname( os.path.realpath(__file__) ),
        header_file
    )

    header = asn1tools.compile_files(header_path, 'uper') 

    @classmethod
    def _get_message_id_scapy(cls, pkt: Packet | RadioTap) -> int:

        # SNAP and Raw are necessary to access to ETSI packages
        if not pkt.haslayer(SNAP) and not pkt.haslayer(Raw): return -1
        
        # if the SNAP code is not 0x8947 the packet not contain an GeoNetwork packet 
        if pkt[SNAP].code != 0x8947: return -1;
            
        geo = GeoNetworking(pkt[Raw].load)
        
        # for CAM and DENM the geo.common_next_header is equal to 2 (BTPb)
        if geo.common_next_header != 2: return -1
        return cls.header.decode('ItsPduHeader', bytes(BTPb(bytes(geo.payload)).payload)).get("messageID")

    @classmethod
    def _get_message_id_pyshark(cls, pkt: packet.Packet) -> int:

        if not hasattr(pkt, "gnw"): return -1
        if not hasattr(pkt.gnw, "ch"): return -1

        # from here is possible to make difference between the btpa or btpb
        nh = getattr(pkt.gnw.ch, "nh", None)
        if nh is None:
            raise Exception("pkt has GeoNetwork layer, but next_header is not specified")

        if not hasattr(pkt.its, "ItsPduHeader_element"):
            raise Exception("pkt has not ItsPduHeader or it is in wrong form - it must be raw")

        # it seems to be necessary to manage both LiveCapture and FileCapture of pyshark
        msg_id = int(getattr(pkt.its.ItsPduHeader_element, "messageId", 0))
        msg_id += int(getattr(pkt.its.ItsPduHeader_element, "messageID", 0)) 

        return msg_id

    @classmethod
    def get_message_id(cls, pkt: packet.Packet | Packet | RadioTap) -> int:
        if isinstance(pkt, packet.Packet):
            return cls._get_message_id_pyshark(pkt)
        if isinstance(pkt, Packet) or isinstance(pkt, RadioTap):
            return cls._get_message_id_scapy(pkt)
        return -1

    @classmethod
    def geo(cls, **kwargs) -> GeoNetworking:
        
        if not all(req in kwargs.keys() for req in required_geo):
            raise Exception(f"missing parameter for create a GeoNetwork frame, need {required_geo}")

        param = { key: kwargs[key] for key in required_geo }
        return GeoNetworking(**param, timestamp=GeoNetworking.get_gn_timestamp())
    
    @classmethod
    def format_msg(cls, tmsg: V2xMsg, **kwargs) -> Packet:

        btpb_raw, pkt_raw = raw(BTPb(destination_port=2001, info=0x5400)), raw(tmsg.encode())
        try:
            geo_raw = raw(cls.geo(
                latitude=tmsg.latitude,
                longitude=tmsg.longitude,
                speed=tmsg.speedValue,
                heading=tmsg.headingValue,
                payload_lenght=len(btpb_raw+pkt_raw),
                **kwargs
            ))
        except AttributeError: raise AttributeError()

        dot11 = Dot11(subtype=8, type=2, proto=0, ID=0, addr1="ff:ff:ff:ff:ff:ff", addr2=kwargs.get("gn_addr_address"), addr3="ff:ff:ff:ff:ff:ff", SC=480)
        qos = Dot11QoS(A_MSDU_Present=0, Ack_Policy=1, EOSP=0, TID=3, TXOP=0)

        llc = LLC(dsap=0xaa, ssap=0xaa, ctrl=3)
        snap = SNAP(OUI=0, code=0x8947)

        mex = Raw(load=geo_raw+btpb_raw+pkt_raw)
        radio = RadioTap(present=0x400000, timestamp=int(time.perf_counter()), ts_accuracy=0, ts_position=0, ts_flags=None)

        return radio / dot11 / qos / llc / snap / mex
