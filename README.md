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

For use the CAM structure is mandatory to have this parameters:

```
header.protocolVersion
header.messageID
header.stationID
cam.generationDeltaTime
cam.camParameters.basicContainer.stationType
cam.camParameters.basicContainer.referencePosition.latitude
cam.camParameters.basicContainer.referencePosition.longitude
cam.camParameters.basicContainer.referencePosition.positionConfidenceEllipse.semiMajorConfidence
cam.camParameters.basicContainer.referencePosition.positionConfidenceEllipse.semiMinorConfidence
cam.camParameters.basicContainer.referencePosition.positionConfidenceEllipse.semiMajorOrientation
cam.camParameters.basicContainer.referencePosition.altitude.altitudeValue
cam.camParameters.basicContainer.referencePosition.altitude.altitudeConfidence
cam.camParameters.highFrequencyContainer.basicVehicleContainerHighFrequency.heading.headingValue
cam.camParameters.highFrequencyContainer.basicVehicleContainerHighFrequency.heading.headingConfidence
cam.camParameters.highFrequencyContainer.basicVehicleContainerHighFrequency.speed.speedValue
cam.camParameters.highFrequencyContainer.basicVehicleContainerHighFrequency.speed.speedConfidence
cam.camParameters.highFrequencyContainer.basicVehicleContainerHighFrequency.driveDirection
cam.camParameters.highFrequencyContainer.basicVehicleContainerHighFrequency.vehicleLength.vehicleLengthValue
cam.camParameters.highFrequencyContainer.basicVehicleContainerHighFrequency.vehicleLength.vehicleLengthConfidenceIndication
cam.camParameters.highFrequencyContainer.basicVehicleContainerHighFrequency.vehicleWidth
cam.camParameters.highFrequencyContainer.basicVehicleContainerHighFrequency.longitudinalAcceleration.longitudinalAccelerationValue
cam.camParameters.highFrequencyContainer.basicVehicleContainerHighFrequency.longitudinalAcceleration.longitudinalAccelerationConfidence
cam.camParameters.highFrequencyContainer.basicVehicleContainerHighFrequency.curvature.curvatureValue
cam.camParameters.highFrequencyContainer.basicVehicleContainerHighFrequency.curvature.curvatureConfidence
cam.camParameters.highFrequencyContainer.basicVehicleContainerHighFrequency.curvatureCalculationMode
cam.camParameters.highFrequencyContainer.basicVehicleContainerHighFrequency.yawRate.yawRateValue
cam.camParameters.highFrequencyContainer.basicVehicleContainerHighFrequency.yawRate.yawRateConfidence
```

For use the DENM structure is mandatory to have this parameters:

```
ITS-Container.header.protocolVersion
ITS-Container.header.messageID
ITS-Container.header.stationID
ITS-Container.denm.management.actionID.originatingStationID
ITS-Container.denm.management.actionID.sequenceNumber
ITS-Container.denm.management.detectionTime
ITS-Container.denm.management.referenceTime
ITS-Container.denm.management.eventPosition.latitude
ITS-Container.denm.management.eventPosition.longitude
ITS-Container.denm.management.eventPosition.positionConfidenceEllipse.semiMajorConfidence
ITS-Container.denm.management.eventPosition.positionConfidenceEllipse.semiMinorConfidence
ITS-Container.denm.management.eventPosition.positionConfidenceEllipse.semiMajorOrientation
ITS-Container.denm.management.eventPosition.altitude.altitudeValue
ITS-Container.denm.management.eventPosition.altitude.altitudeConfidence
ITS-Container.denm.management.validityDuration
ITS-Container.denm.management.stationType
```

In both case the input file for the `V2xAsnP` must be compliant with the usage of the ETSI-ITS standard, one file with the structure of the message and the other with the datatype, and the parameter must be pass like `protocolVersion=1`

### Important
For using this script you must have the `interface` set into monitoring in mode **Outside The Context of a BSS (OCB)**, and set the python interpreter with the rigth capabilities:
```bash
sudo setcap 'cap_net_raw=eip' /usr/bin/python3.x
```
