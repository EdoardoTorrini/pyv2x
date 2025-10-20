from scapy.packet import Packet
from scapy.sendrecv import sendp, sniff

from threading import Thread, Semaphore
from typeguard import typechecked
from queue import Queue, Empty

from pyv2x.etsi import ETSI, V2xTMsg
from pyv2x.v2x_cam import CAM
from pyv2x.v2x_denm import DENM

import pyshark
from pyshark.packet import packet

import time
import asn1tools
import sys

# TODO: change the logic behind the parsing of msg, pass only the its_raw.value into the Queue
# remove the cparser e dparser, on top of that we can identify the message type
required = [ "interface", "cparser", "dparser" ]

@typechecked
class V2xNetwork:

    def __init__(self, **kwargs):

        if not all(item in kwargs.keys() for item in required):
            raise Exception(f"wrong definition of V2xNetwork: {required}")
        
        self.__dict__.update(kwargs)
        
        if not isinstance(self.cparser, asn1tools.compiler.Specification):
            raise Execption("cparser must be asn1tools.compiler.Specification - with CAM asn.1")

        if not isinstance(self.dparser, asn1tools.compiler.Specification):
            raise Exception("dparser must be asn1tools.compiler.Specification - with DENM asn.1") 

        self._queue = Queue(maxsize=0)
        tshark = Thread(target=self.start_listener_v2x, daemon=True).start()

    def send_msg(self, packet: Packet) -> None:
        sendp(packet, iface=self.interface)

    def start_listener_v2x(self):
        self._trace = pyshark.LiveCapture(interface=self.interface)
        for pkt in self._trace.sniff_continuously():
            # TODO: self._queue.put(bytes.fromhex(pkt.its_raw.value)
            msg = None
            try: 
                nh = ETSI.get_message_id(pkt)
                match nh:
                    case V2xTMsg.ETSI_DENM:
                        continue
                    case V2xTMsg.ETSI_CAM:
                        msg = ETSI.format_msg(self.cparser, CAM, **dict(CAM(flat=pkt)))
            except Exception as e:
                # print(f"error: {str(e)}", file=sys.stderr)
                continue

            if msg is not None:
                self._queue.put(msg)

            time.sleep(0.1)
    
    def is_empty(self) -> bool:
        return self._queue.empty()

    def get_new_msg(self) -> packet.Packet | Packet | None:
        try:
            return self._queue.get_nowait()
        except Empty:
            return None
        except Exception as e:
            raise Exception(str(e))
