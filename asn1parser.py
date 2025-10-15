from flatdict import FlatDict
from typeguard import typechecked
import os
import asn1tools


@typechecked
class V2xAsnP:

    _ac_datatype = ["INTEGER", "ENUMERATED", "BIT STRING"]
    _get_key = lambda x: os.path.splitext(os.path.basename(x))[0]

    _keys = []
    _keys_structure = []
    _keys_datatype = []
    _flat_dict = {}
    _tree = {}
    _imports = []

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

    def _parser_structure(self) -> dict:
        _tree_= {} 
        for k in self._keys_structure:
            structure = FlatDict(self._dspec.get(k), delimiter=".")
            for root in self._keys_datatype:
                self._tree = {self._name: root}
                for key in structure.keys():
                    if key.split(".")[-1] != "members":
                        continue
                    if key.split(".")[1] in self._tree.keys():
                        root = self._tree[key.split(".")[1]]
                    for member in structure.get(key):
                        try:
                            if member.get("type") not in self._tree.keys():
                                self._tree[member.get("type")] = root + "." + member.get("name")
                            if member.get("type") in self._imports: 
                                _tree_[root + "." + member.get("name")] = member.get("type")
                            elif f"types.{member.get("type")}.members" not in structure.keys():
                                _tree_[root + "." + member.get("name")] = structure.get(f"types.{member.get("type")}.type")
                        except: continue
        return _tree_
    
    def _parser_datatype(self, trees: dict):
        for root in self._keys_datatype:
            datatype = FlatDict(self._dspec.get(root), delimiter=".")
            for leaf, t in trees.items():
                if t in self._ac_datatype:
                    self._flat_dict[leaf] = t
                elif f"types.{t}.members" in datatype.keys():
                    self.find_leaf_type(datatype, datatype.get(f"types.{t}.members"), leaf, t)
                elif f"types.{t}.type" in datatype.keys():
                    self.find_leaf_type(datatype, {}, leaf, datatype.get(f"types.{t}.type"), t)

    # TODO: finish
    def find_leaf_type(self, all: FlatDict | dict, sub: dict | list, base_name: str, base_type: str, old_type: str = "") -> int:        
        try:
            if base_type in self._ac_datatype:
                if base_type == "ENUMERATED": 
                    self._flat_dict[base_name] = {"type": base_type, "value": all.get(f"types.{old_type}.values")}
                else: 
                    self._flat_dict[base_name] = base_type
                return 0
            if isinstance(sub, list):
                for el in sub:
                    if el is None: return 0
                    self.find_leaf_type(all, el, base_name + "." + el.get("name"), el.get("type"), base_type)
            if isinstance(sub, dict):
                if f"types.{base_type}.members" in all.keys():
                    self.find_leaf_type(all, all.get(f"types.{base_type}.members"), base_name, base_type, base_type)
                elif f"types.{base_type}.type" in all.keys():
                    self.find_leaf_type(all, {}, base_name, all.get(f"types.{base_type}.type"), base_type)
        except Exception as e: pass
        return 0


    def create_class(self):
        return type(self._name, (V2xMsg,), {
            "name": self._name,
            "_required": self.req,
            "_spec": asn1tools.compile_dict(self._dspec),
            "_flat_dict": self._flat_dict
        })

class V2xMsg:

    def __init__(self, **kwargs):

        if "raw_bytes" in kwargs.keys():
            try: 
                self._spec.decode(self._name, kwargs.get("raw_bytes"))
            except: raise Exception("generic error")

        if not all(req in kwargs for req in self._cam_req):
            raise Exception(f"Missing parameter for CAM frame, need: {self._cam_req}")


files = ["./asn/cam/CAM-PDU-Descriptions.asn", "./asn/cam/cdd/ITS-Container.asn"]
spec = V2xAsnP.new("CAM", files)
CAM = spec.create_class()

exit()
