from scapy.packet import Packet
from scapy.sendrecv import sendp, sniff, AsyncSniffer

from threading import Thread, Semaphore
from typeguard import typechecked
from queue import Queue, Full, Empty

from pyv2x.etsi import ETSI, ETSI_CAM, ETSI_DENM

import time


required = [ "interface" ]

@typechecked
class V2xNetwork:

    def __init__(self, **kwargs):

        if not all(item in kwargs.keys() for item in required):
            raise Exception(f"wrong definition of V2xNetwork: {required}")
        
        self.__dict__.update(kwargs)

        self._queue = Queue(maxsize=100)
        self._tshark = AsyncSniffer(iface=self.interface, prn=self.callback, store=False, monitor=True)
        self._tshark.start()
        # Thread(target=self.start_v2x_listener, daemon=True).start()

    # def start_v2x_listener(self):
    #     while True:
    #         self._tshark = AsyncSniffer(iface=self.interface, prn=self.callback, store=False, monitor=True)
    #         self._tshark.start()
    #         time.sleep(1)
    #         self._tshark.stop()


    def send_msg(self, packet: Packet) -> None:
        sendp(packet, iface=self.interface)
    
    def callback(self, packet: Packet):
        try:
            self._queue.put(packet)
        except Full:
            self._queue.get_nowait()
            self._queue.put_nowait(packet)
        except Exception as e:
            raise Exception(f"callback exception: {str(e)}")
    
    def is_empty(self) -> bool:
        return self._queue.empty()

    def get_new_msg(self) -> Packet | None:
        try:
            return self._queue.get_nowait()
        except Empty:
            return None 
        except Exception as e:
            raise Exception(f"get_new_msg execption: {str(e)}")
