from scapy.packet import Packet
from scapy.sendrecv import sendp, sniff

from threading import Thread, Semaphore
from typeguard import typechecked
from queue import Queue

from pyv2x.etsi import ETSI

required = [ "interface" ]

@typechecked
class V2xNetwork:

    _sem = Semaphore(1)
    _queue = Queue(maxsize=0)


    def __init__(self, **kwargs):

        if not all(item in kwargs.keys() for item in required):
            raise Exception(f"wrong definition of V2xNetwork: {required}")
        
        self.__dict__.update(kwargs)
        tshark = Thread(self.start_listener_v2x, daemon=True).start()

    def send_msg(self, packet: Packet) -> None:
        sendp(packet, iface=self.interface)

    def start_listener_v2x(self):
        sniff(iface=self.interface, prn=self.callback, count=10)

    def callback(self, packet: Packet):
        # TODO: check if is CAM or DENM
        pass
