from scapy.packet import Packet
from scapy.sendrecv import sendp, sniff

from threading import Thread, Semaphore
from typeguard import typechecked
from queue import Queue, Empty

from pyv2x.etsi import ETSI, ETSI_CAM, ETSI_DENM

import pyshark
from pyshark.packet import packet
import time


required = [ "interface" ]

@typechecked
class V2xNetwork:

    def __init__(self, **kwargs):

        if not all(item in kwargs.keys() for item in required):
            raise Exception(f"wrong definition of V2xNetwork: {required}")
        
        self.__dict__.update(kwargs)
        self._queue = Queue(maxsize=0)
        tshark = Thread(target=self.start_listener_v2x, daemon=True).start()

    def send_msg(self, packet: Packet) -> None:
        sendp(packet, iface=self.interface)

    def start_listener_v2x(self):
        self._trace = pyshark.LiveCapture(interface=self.interface)
        for pkt in self._trace:
            nh = ETSI.get_message_id(pkt)
            self._queue.put(pkt)
            time.sleep(0.1)
    
    def is_empty(self) -> bool:
        return self._queue.empty()

    def get_new_msg(self) -> packet.Packet | None:
        try:
            return self._queue.get_nowait()
        except Empty:
            return None
        except Exception as e:
            raise Exception(str(e))
