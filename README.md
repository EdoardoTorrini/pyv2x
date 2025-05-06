# pyV2X
Library for the sending and receiving the CAM, DENM message through the api. The full implementation is in python every contribution are welcome following few simple rules:
* create its own branch for the developing
* follow the standard definded into the [cam documentation](./doc/etsi_its_cam.pdf) and [denm documentation](./doc/etsi_its_denm.pdf)

## Examples
* send CAM message
```python
from pyv2x.etsi import ETSI
from pyv2x.v2x_utils import GeoNetworking

import asn1tools

interface = "wlan0"
latitude = 446351418
longitude = 108136683
speed = 50
heading = 0
timestamp = GeoNetworking.get_gn_timestamp()
altitude = 0
mac_address = 'b4:b5:b6:c4:11:49'

cam_spec = asn1tools.compile_files('asn/cam.asn', 'uper')

cam_msg = ETSI.new_cam(
    cam_spec, gn_addr_address=mac_address, station_id=4935, latitude=latitude, longitude=longitude,
    delta_time=timestamp, speed=speed, heading=heading
)
net.send_msg(cam_msg)
```

* send DENM message
```python
from pyv2x.etsi import ETSI
from pyv2x.v2x_utils import GeoNetworking

import asn1tools

interface = "wlan0"
latitude = 446351418
longitude = 108136683
speed = 50
heading = 0
timestamp = GeoNetworking.get_gn_timestamp()
altitude = 0
mac_address = 'b4:b5:b6:c4:11:49'

denm_spec = asn1tools.compile_files('asn/denm.asn', 'uper')

denm_msg = ETSI.new_denm(
    denm_spec, gn_addr_address=mac_address, station_id=4825, latitude=latitude, longitude=longitude,
    delta_time=timestamp, distance="lessThan200m", traffic_direction="allTrafficDirections", speed=speed, heading=heading
)
net.send_msg(denm_msg)
```

* receiving DENM, CAM msg from the network
```python
from pyv2x.etsi import ETSI, ETSI_CAM, ETSI_DENM
from pyv2x.v2x_network import V2xNetwork

import asn1tools

cam_spec = asn1tools.compile_files('asn/cam.asn', 'uper')
denm_spec = asn1tools.compile_files('asn/denm.asn', 'uper')

interface = "wlan0"
net = V2xNetwork(interface=interface)

try:
    while 1:
        if not net.is_empty():
            type_, msg = net.get_new_msg()

            if type_ == ETSI_CAM:
                data = ETSI.get_cam_payload(msg, cam_spec)

            if type == ETSI_DENM:
                data = ETSI.get_denm_payload(msg, denm_spec)
                
            print(f"message type: {type_}")
            from pprint import pprint
            pprint(data)

except KeyboardInterrupt:
    exit()
```

### Important
For using this script you must have the `interface` set into monitoring in mode **Outside The Context of a BSS (OCB)**, and set the python interpreter with the rigth capabilities:
```bash
sudo setcap 'cap_net_raw=eip' /usr/bin/python3.x
```