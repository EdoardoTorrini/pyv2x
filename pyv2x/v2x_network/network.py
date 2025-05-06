from scapy.packet import Packet
from scapy.sendrecv import sendp, sniff

from threading import Thread, Semaphore
from typeguard import typechecked
from queue import PriorityQueue

from pyv2x.etsi import ETSI, ETSI_CAM, ETSI_DENM


required = [ "interface" ]

@typechecked
class V2xNetwork:

    _queue = PriorityQueue(maxsize=0)


    def __init__(self, **kwargs):

        if not all(item in kwargs.keys() for item in required):
            raise Exception(f"wrong definition of V2xNetwork: {required}")
        
        self.__dict__.update(kwargs)
        tshark = Thread(target=self.start_listener_v2x, daemon=True).start()

    def send_msg(self, packet: Packet) -> None:
        sendp(packet, iface=self.interface)

    def start_listener_v2x(self):
        sniff(iface=self.interface, prn=self.callback, count=10)

    def callback(self, packet: Packet):        
        match ETSI.get_message_id(packet):
            case 1:
                self._queue.put((ETSI_DENM, packet))
            case 2:
                self._queue.put((ETSI_CAM, packet))
            case _:
                pass
    
    def is_empty(self) -> bool:
        return self._queue.empty()

    def get_new_msg(self) -> tuple:
        return self._queue.get()
