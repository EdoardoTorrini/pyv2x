from scapy.all import Packet, ShortField


class BTPa(Packet):
    name = "BTPa"
    fields_desc = [
        ShortField("destination_port", 0),
        ShortField("sequence_number", 0)
    ]


class BTPb(Packet):
    name = "BTPb"
    fields_desc = [
        ShortField("destination_port", 0),
        ShortField("info", 0)
    ]