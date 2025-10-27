from flatdict import FlatDict
from typeguard import typechecked
from typing import Iterable
import os
import asn1tools

from pyv2x.v2x_msg import V2xMsg
from scapy.packet import Packet as p_scapy
from pyshark.packet.packet import Packet as p_pyshark


@typechecked
class V2xAsnP:

    # TODO: make config the _ac_datatype
    _ac_datatype = ["INTEGER", "ENUMERATED", "BIT STRING", "OCTET STRING", "IA5String", "UTF8String", "NumericString"]
    _get_key = lambda x: os.path.splitext(os.path.basename(x))[0]

    def __init__(self):
        self._keys = []
        self._keys_structure = []
        self._keys_datatype = []
        self._flat_dict = {}
        self._tree = {}
        self._imports = []
        self._choice = {}
        
        self._optional = []

    @classmethod
    def new(cls, name: str, file: list | str) -> "V2xAsnP":

        asn_parser = cls()
        asn_parser._name = name
        path_to_asn1 = [file] if isinstance(file, str) else file
        for file in path_to_asn1:
            if not os.path.exists(file):
                raise FileNotFoundError(f"file: {file} not found")
            
            asn_parser._keys.append(cls._get_key(file))

        asn_parser._dspec = asn1tools.parse_files(path_to_asn1)
        
        btree = None
        if asn_parser._check_imports():
            btree = asn_parser._parser_structure()

        asn_parser._parser_datatype(btree)
        return asn_parser
    
    def _check_imports(self) -> bool:
        for key in self._keys:
            flat, tmp = FlatDict(self._dspec.get(key), delimiter="."), self._keys.copy()
            tmp.remove(key)
            for el in tmp:
                if f"imports." + el in flat.keys():
                    self._tree = {self._name: el}
                    self._imports.extend(flat.get(f"imports." + el))
                    self._keys_structure.append(key)
        
        self._imports = list(set(self._imports))
        self._keys_datatype = list(set([ x for x in self._keys if x not in self._keys_structure ]))
        self._keys_structure = list(set(self._keys_structure))
        return len(self._imports) != 0

    def _sort(self, data: Iterable) -> list:
        return sorted(
            data,
            key=lambda x: x[1] if isinstance(x, tuple) and len(x) > 1 else float('-inf'),
            reverse=True
        )

    def _parser_structure(self) -> dict:
        _tree_= {} 
        for k in self._keys_structure:
            structure = FlatDict(self._dspec.get(k), delimiter=".")
            for root in self._keys_datatype:
                self._tree = {self._name: root}
                
                for key in structure.keys():
                    if key.split(".")[-1] != "members": continue

                    if structure.get(f"types.{key.split('.')[1]}.type") == "CHOICE":
                       self._choice[ self._tree.get(key.split(".")[1]).split(".")[-1] ] = [ value.get("name") for value in structure.get(f"types.{key.split('.')[1]}.members")[:-1] ] 
                    
                    if key.split(".")[1] in self._tree.keys(): root = self._tree[key.split(".")[1]]
                    
                    for member in structure.get(key):
                        try:
                            if member.get("optional") == True: 
                                
                                self._optional.append(member.get('name')) #TODO non resiste se esistono due campi con lo stesso nome (imposti entrambi a optional anche se solo uno lo è)

                            if member.get("type") not in self._tree.keys():
                                self._tree[member.get("type")] = root + "." + member.get("name")


                            if member.get("type") in self._imports: 
                                _tree_[root + "." + member.get("name")] = member.get("type")
                            elif f"types.{member.get('type')}.members" not in structure.keys():
                                _tree_[root + "." + member.get("name")] = structure.get(f"types.{member.get('type')}.type")
                        except: continue
        return _tree_
   
    # TODO: PathHistory::= SEQUENCE (SIZE(0..40)) OF PathPoint -> this type is managed wrong
    def _parser_datatype(self, trees: dict):
        
        for root in self._keys_datatype:
            datatype = FlatDict(self._dspec.get(root), delimiter=".")
            for leaf, t in trees.items():
                opt = True if leaf.split('.')[-1] in self._optional else False
                if t in self._ac_datatype:
                    self._flat_dict[leaf] = { "type": t, "optional": opt  }#todo qui
                elif f"types.{t}.members" in datatype.keys():
                    self.find_leaf_type(datatype, datatype.get(f"types.{t}.members"), leaf, t, opt=opt)
                elif f"types.{t}.type" in datatype.keys():
                    self.find_leaf_type(datatype, {}, leaf, datatype.get(f"types.{t}.type"), t, opt=opt)
        

    # TODO: remove hardcoded "optional": True
    def find_leaf_type(self, all: FlatDict | dict, sub: dict | list, base_name: str, base_type: str, old_type: str = "", opt: bool = False) -> int:        
        try:
            if base_type in self._ac_datatype:
                
                match base_type:
                    case "ENUMERATED":
                        val = all.get(f"types.{old_type}.values")
                        self._flat_dict[base_name] = {
                            "type": base_type,
                            "value": val,
                            "optional": opt,
                            "default": self._sort(val)[0][0]
                        }
                    case "BIT STRING":
                        size = all.get(f"types.{old_type}.size")[0]
                        self._flat_dict[base_name] = {
                            "type": base_type,
                            "length": size,
                            "info": all.get(f"types.{old_type}.named-bits"),
                            "optional": opt,
                            "default": (b"\x00", 8)
                        }
                    case "INTEGER":
                        self._flat_dict[base_name] = {
                            "type": base_type,
                            "optional": opt,
                            "default": 0
                        }
                    case "OCTET STRING":
                        self._flat_dict[base_name] = {
                            "type": base_type,
                            "optional": opt,
                            "default": b"\x00"
                        }
                    case _:
                        self._flat_dict[base_name] = {
                            "type": base_type,
                            "optional": opt
                        }
                return 0
            if isinstance(sub, list):
                for el in sub:
                    if el is None: return 0
                    self.find_leaf_type(all, el, base_name + "." + el.get("name"), el.get("type"), base_type, opt=opt)
            if isinstance(sub, dict):
                if f"types.{base_type}.members" in all.keys():
                    self.find_leaf_type(all, all.get(f"types.{base_type}.members"), base_name, base_type, base_type, opt=opt)
                elif f"types.{base_type}.type" in all.keys():
                    self.find_leaf_type(all, {}, base_name, all.get(f"types.{base_type}.type"), base_type, opt=opt)
        except Exception as e: pass
        return 0


    def create_class(self):
        return type(self._name, (V2xMsg,), {
            "name": self._name,
            "_required": [ key.split(".")[-1] for key in self._flat_dict if self._flat_dict.get(key).get("optional") == False ],
            "_spec": asn1tools.compile_dict(self._dspec, "uper"),
            "_flat_dict": self._flat_dict,
            "_choice": self._choice
        })

