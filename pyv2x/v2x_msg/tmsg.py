from pyv2x.v2x_utils import GeoNetworking, BTPb
from scapy.packet import Packet as p_scapy
from scapy.packet import Raw
from pyshark.packet.packet import Packet as p_pyshark

from typeguard import typechecked
from flatdict import FlatDict


@typechecked
class V2xMsg:
    _is_raw = False
    _raw_data = None
    
    # TODO: make more specific the raise error
    def __init__(self, **kwargs):

        self._find_leaf_duplicate()
        if "pkt" in kwargs.keys():
            try:
                self._pkt = kwargs.get("pkt")
                self._is_raw = True
                if not isinstance(self._pkt, p_scapy) and not isinstance(self._pkt, p_pyshark):
                    raise Exception("generic error")
                self._decode()
            except: raise Exception("generic error")
        
        else:
            if not all(req in kwargs for req in self._required):
                raise Exception(f"Missing parameter for {self.name} frame, need: {self._required}")
             
            for k, v in kwargs.items():
                if k in self._duplicate: raise Exception(f"{k} is ambiguos, specifies the path [ father_{k} ]")

            self.__dict__.update(**kwargs)

    def _find_leaf_duplicate(self):
        t, tm = [ key.split(".")[-1] for key, val in self._flat_dict.items() ], {}
        for el in t:
            if el not in tm.keys(): tm[el] = 1
            else: tm[el] += 1

        t = [ k for k, v in tm.items() if v != 1 ]
        self._duplicate = t


    def __iter__(self):
        t = { key if not key.find("_") > -1 else key.replace("_", "."): val  for key, val in self.__dict__.items() if not key.startswith("_") }
        return iter(t.items())

    def __repr__(self):
        return "".join([ f"{key}: {val}\n" for key, val in dict(self).items() if not key.startswith("_") ])

    def _get_val(self, desc: dict, k: str): 
        default = desc.get("default") if "default" in desc.keys() else None
        val = dict(self).get(k, default)
        return val

    def as_dict(self):

        # TODO: the field CHOICE in the asn1 is not managed correctly
        # for semplicity I have omitted the sequence field optional in the CamParameters
        tmp, choice_base, all_base = {}, {}, {}
        for k, val in {a: self._choice.get(a) for a in list(self._choice.keys())[:1]}.items():
            for key in self._flat_dict.keys():
                if key.find(k) > -1:
                    l = key.split(f".{k}.")
                    nkey = l[0] + "." + k
                    if l[1].split(".")[-1] in self._required or l[1].split(".")[-1] in self.__dict__.keys():
                        if nkey not in tmp.keys(): tmp[ nkey ] = (val[0], {".".join( l[1].split(".")[1:] ): self._get_val(self._flat_dict.get(key), key.split(".")[-1])} )
                        else: tmp[ nkey ][1][".".join( l[1].split(".")[1:] )] = self._get_val(self._flat_dict.get(key), key.split(".")[-1])

        for key, value in tmp.items():
            choice_base[ key ] = (value[0], FlatDict(value[1], delimiter=".").as_dict())

        for key, value in self._flat_dict.items():
            if all([ not key.find(k) > -1 for k in self._choice.keys() ]) and key not in all_base.keys():
                
                for k in dict(self):
                    for kf, kc in zip(k.split(".")[::-1], key.split(".")[::-1]):
                        if kf != kc: break
                    else:
                        kd = key.split(".")[-1] if len(k) == 1 else k
                        all_base[key] = self._get_val(value, kd)

                    if key in all_base.keys(): break

        all_base.update(choice_base)

        return FlatDict({".".join(key.split(".")[1:]): value for key, value in all_base.items()}, delimiter=".").as_dict()        

    def encode(self):
        return self._spec.encode(self.name, self.as_dict()) 
    
    def _map_data_to_class(self, tmp):
        for key, value in self._flat_dict.items():
            nk, base, i = key.split(".")[1:], tmp, 0
            while i < len(nk):
                if not isinstance(base, dict): break
                if nk[i] in self._choice.keys():
                    base = base.get(nk[i], [None, None])[1]
                    i += 1
                else: 
                    base = base.get(nk[i], value.get("default"))
                i += 1
            if nk[-1] in self._required or (base != self._get_val(value, ".".join(nk)) and not self._is_raw):
                k = nk[-1] if nk[-1] not in self._duplicate else ".".join(nk)
                self.__dict__.update(**{k: base})

    def _decode(self):
        data = None
        match self._pkt:
            case p_scapy():
                data = self._spec.decode(self.name, bytes(BTPb(bytes(GeoNetworking(self._pkt[Raw].load).payload)).payload))
            case p_pyshark():
                data = self._spec.decode(self.name, bytes.fromhex(self._pkt.its_raw.value))
        if data is not None: self._map_data_to_class(data)

    def get_id(self): return self._get_val(dict(self), "messageID")
