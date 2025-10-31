# pyV2X
Library for the sending and receiving the CAM, DENM message through the api. The full implementation is in python every contribution are welcome following few simple rules:
* create its own branch for the developing
* follow the standard definded into the [cam documentation](./doc/etsi_its_cam.pdf) and [denm documentation](./doc/etsi_its_denm.pdf)

## Installation
Download the last release and execute into a terminal:
```bash 
$ python -m pip install ./pyv2x.whl
```

## Example
For the example check the `main.py` file

### Important
For using this script you must have the `interface` set into monitoring in mode **Outside The Context of a BSS (OCB)**, and set the python interpreter with the rigth capabilities:
```bash
sudo setcap 'cap_net_raw=eip' /usr/bin/python3.x
```
