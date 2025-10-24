from scapy.packet import Packet as p_scapy
from scapy.sendrecv import sendp, sniff

from pyshark.packet.packet import Packet as p_pyshark

from threading import Thread
from typeguard import typechecked
from typing import List, Type
from queue import Queue, Empty

from pyv2x.etsi import ETSI, V2xTMsg
from pyv2x.v2x_msg import V2xMsg

import pyshark

import time
import asn1tools
import sys



# TODO: change the logic behind the parsing of msg, pass only the its_raw.value into the Queue
# remove the cparser e dparser, on top of that we can identify the message type

@typechecked
class V2xNetwork:

    def __init__(self, iface: str, ltmsg: List[Type[V2xMsg]], filter: str = "its"):
        
        if len(V2xTMsg) < len(ltmsg):
            raise Exception(f"the size of V2xTMsg is {len(V2xTMsg)} and support this type of msg: {' '.join([ v for k, v in dict(V2xTMsg).items() ])}")

        self._ltmsg, self._iface = {}, iface
        for tmsg in ltmsg:
            if not hasattr(tmsg, "name"):
                raise Exception("wrong type class")
            self._ltmsg[ V2xTMsg.get(tmsg.name) ] = tmsg

        self._queue = Queue(maxsize=0)
        self._filter = filter
        tshark = Thread(target=self.start_listener_v2x, daemon=True).start()

    def send_msg(self, packet: p_scapy) -> None:
        sendp(packet, iface=self._iface)

    def start_listener_v2x(self):
        self._trace = pyshark.LiveCapture(interface=self._iface, use_json=True, include_raw=True, display_filter=self._filter)
        for pkt in self._trace.sniff_continuously():
            try: 
                nh = ETSI.get_message_id(pkt)
                for id, tmsg in self._ltmsg.items():
                    if id == nh:
                        msg = tmsg(pkt=pkt)
                        break
                else:
                    msg = None
            except Exception as e:
                # print(f"error: {str(e)}", file=sys.stderr)
                continue

            if msg is not None:
                self._queue.put(msg)

            time.sleep(0.1)
    
    def is_empty(self) -> bool:
        return self._queue.empty()

    def get_new_msg(self) -> V2xMsg | None:
        try:
            return self._queue.get_nowait()
        except Empty:
            return None
        except Exception as e:
            raise Exception(str(e))
