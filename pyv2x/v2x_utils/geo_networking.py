from scapy.all import Packet, BitField, MACField

import json
import time
from datetime import datetime, timezone


class GeoNetworking(Packet):
    name = "GeoNetworking"
    fields_desc = [
        
        # Basic Header 
        BitField("version", 1, 4),
        BitField("basic_next_header", 1, 4),
        BitField("reserved", 0, 8),
        BitField("life_time_multiplier", 60, 6, 8), 
        BitField("life_time_base", 1, 2), 
        BitField("remaining_hop_limit", 1, 8),

        # Common Header
        BitField("common_next_header", 2, 4), 
        BitField("h_reserved", 0, 4),
        BitField("header_type", 5, 4),
        BitField("header_sub_type", 0, 4),
        BitField("traffic_story_carry_forward", 0, 1),
        BitField("traffic_channel_offload", 0, 1),
        BitField("traffic_class_id", 2, 6),
        BitField("mobility_flags", 0, 1),
        BitField("flags_reserved", 0, 7),
        BitField("payload_lenght", 50, 16),
        BitField("maximum_hop_limit", 1, 8),
        BitField("Reserved", 0, 8),

        # geo networking for cam and denm
        BitField("gn_addr_manual", 0, 1),
        BitField("gn_addr_its_type", 15, 5),
        BitField("gn_addr_its_country_code", 0, 10),
        MACField("gn_addr_address", None),
        BitField("timestamp", None, 32),
        BitField("latitude", None, 32),
        BitField("longitude", None, 32),
        BitField("position_accuracy_indicator", 0, 1),
        BitField("speed", None, 15),
        BitField("heading", None, 16),

        BitField('local_channel_busy_ratio', 0, 8),
        BitField('max_neighbouring_cbr', 0, 8),
        BitField('output_power', 23, 5),
        BitField('reserved_tsbp', 0, 3),
        BitField('reserved_tsbp_2', 0, 8),
    ]
    
    def get_data(self):
        return json.loads(self.json())
    
    @classmethod
    def get_gn_timestamp(cls):
        # Epoch ITS: 2004-01-01 00:00:00 UTC
        return int(
            (
                datetime.now(timezone.utc) - 
                datetime(2004, 1, 1, tzinfo=timezone.utc)
            ).total_seconds() * 1000
        ) & 0xFFFFFFFF