#pragma once

#include <stdlib.h>
#include <stdint.h>

namespace ETSI {

    enum class ITS_STATION_TYPE {
        PERSONAL = 1,
        ROAD_SIDE,
        VEHICLE,
        OTHER
    };

    /**
     * @brief: CAM vehicle profiles supported
     * @exception: it is mandatory to support only one of these type
     */
    enum class CAM_VEHICLE_PROFILE {
        PUBLIC_TRANSPORT = 1,
        SPECIAL_TRANSPORT,
        DANGEROUS_GOODS,
        ROAD_WORK,
        RESCUE,
        EMERGENCY,
        SAFETY_CAR,
        BASIC_VEHICLE
    };

    enum class CAM_DRIVE_DIRECTION {
        FORWARD = 0,
        BACKWARD,
        UNAVAILABLE,
    };

    enum class CURVATURE_CONFIDENCE {
        ONE_PER_METER_0_00002 = 0,
        ONE_PER_METER_0_0001,
        ONE_PER_METER_0_0005,
        ONE_PER_METER_0_002,
        ONE_PER_METER_0_01,
        ONE_PER_METER_0_1,
        OUT_OF_RANGE,
        UNAVAILABLE,
    };

    enum class CURVATURE_CALCULATION_MODE {
        YAW_RATE_USED = 0,
        YAW_RATE_NOT_USED,
        TRANSITION_MODE,
    };

    enum class YAW_RATE_CONFIDENCE {
        DEG_SEC_000_01 = 0,
        DEG_SEC_000_05,
        DEG_SEC_000_10,
        DEG_SEC_001_00,
        DEG_SEC_005_00,
        DEG_SEC_010_00,
        DEG_SEC_100_00,
        OUT_OF_RANGE,
        UNAVAILABLE,
    };

    enum class VEHICLE_LENGTH_CONF_INDICATOR {
        NO_TRAILER_PRESENT = 0,
        TRAILER_PRESENT_WITH_KNOWN_LENGTH,
        TRAILER_PRESENT_WITH_UNKNOWN_LENGTH,
        TRAILER_PRESENCE_IS_UNKNOWN,
    };

    enum class ALTITUDE_CONFIDENCE {
        ALT_000_01 = 0,
        ALT_000_02,
        ALT_000_05,
        ALT_000_10,
        ALT_000_20,
        ALT_000_50,
        ALT_001_00,
        ALT_002_00,
        ALT_005_00,
        ALT_010_00,
        ALT_020_00,
        ALT_050_00,
        ALT_100_00,
        ALT_200_00,
        OUT_OF_RANGE,
        UNAVAILABLE,
    };

    typedef struct {
        /**
         * @brief: { wgs84North(0), wgs84East(900), wgs84South(1800), wgs84West(2700), unavailable(3600)}
         */
        int headingValue;

        /**
         * @brief: { withinZeroPointOneDegree(1), withinOneDegree(10), outOfRange(126), unavailable(127) }
         */
        int headingConfidence;
    } heading_t;

    typedef struct {
        /**
         * @brief: { standstill(0), oneCentimeterPerSec(1), unavailable(16 383) }
         */
        int speedValue;

        /**
         * { withinOneCentimeterPerSec(1), withinOneMeterPerSec(100), outOfRange(126), unavailable(127) }
         */
        int speedConfidence;
    } speed_t;

    typedef struct {
        /**
         * @brief: { pointOneMeterPerSecSquaredForward(1),pointOneMeterPerSecSquaredBackward(-1), unavailable(161) }
         */
        int longitudinalAccelerationValue;

        /**
         * @brief:  pointOneMeterPerSecSquared(1), outOfRange(101), unavailable(102) }
         */
        int longitudinalAccelerationConfidence;
    } longitudinal_acceleration_t;

    typedef struct {
        /**
         * @brief: { straight(0), reciprocalOf1MeterRadiusToRight(-30 000), reciprocalOf1MeterRadiusToLeft(30 000), unavailable(30001) }
         */
        int curvatureValue;

        /**
         * @brief: 
         */
        CURVATURE_CONFIDENCE curvatureConfidence;
    } curvature_t;

    typedef struct {
        /**
         * @brief: { straight(0), degSec-000-01ToRight(-1),degSec-000-01ToLeft(1), unavailable(32 767) }
         * LSB units of 0,01 degrees per second
         */
        int yawRateValue;
        YAW_RATE_CONFIDENCE yawRateConfidence;
    } yaw_rate_t;
    
    typedef struct {
        /**
         * @brief: { tenCentimeters(1), outOfRange(1 022), unavailable(1 023) }
         */
        int vehicleLengthValue;
        VEHICLE_LENGTH_CONF_INDICATOR vehicleLengthConfidenceIndication;
    } vehicle_length_t;

    typedef struct {
        /**
         * @brief: { oneCentimeter(1), outOfRange(4 094), unavailable(4 095) } 
         */
        int semiMajorConfidence;

        /**
         * @brief: { oneCentimeter(1), outOfRange(4 094), unavailable(4 095) }
         */
        int semiMinorConfidence;

        /**
         * @brief: heading
         */
        int semiMajorOrientation;
    } position_confidence_ellipse_t;

    typedef struct {
        /**
         * @brief: { seaLevel(0), oneCentimeter(1), unavailable(800 001) }
         */
        int altitudeValue;

        ALTITUDE_CONFIDENCE altitudeConfidence;

    } altitude_t;

    class PduHeader {

        private:
            uint8_t m_protocolVersion, m_messageId;
            int m_stationId;

        public:
            PduHeader(uint8_t version, uint8_t mId, int sId)
                :  m_protocolVersion(version), m_messageId(mId), m_stationId(sId) {}
    };

    class ReferencePosition {

        private:
            int latitude, longitude;
            position_confidence_ellipse_t positionConfidenceEllipse;
            altitude_t altitude;
        public:
            ReferencePosition(int lat, int longi, position_confidence_ellipse_t conf_pos, altitude_t alt)
                : latitude(lat), longitude(longi), positionConfidenceEllipse(conf_pos), altitude(alt) {}
    };

    class BasicContainer {
        
        private:
            ITS_STATION_TYPE m_type;
            ReferencePosition m_referencePosition;

        public:
            BasicContainer(ITS_STATION_TYPE type, ReferencePosition ref)
                : m_type(type), m_referencePosition(ref) {}
    };

    class BasicVehicleContainerHighFrequency {

        private:
            heading_t heading;
            speed_t speed;
            CAM_DRIVE_DIRECTION driveDirection;
            vehicle_length_t vehicleLength;
            longitudinal_acceleration_t longitudinalAcceleration;
            curvature_t curvature;
            CURVATURE_CALCULATION_MODE curvatureCalculationMode;
            yaw_rate_t yawRate;
            
            /**
             * @brief: { tenCentimeters(1), outOfRange(61), unavailable(62) }
             */
            int vehicleWidth;
        
        public:
            BasicVehicleContainerHighFrequency(heading_t h, speed_t s, CAM_DRIVE_DIRECTION drive_direction, vehicle_length_t length, 
                longitudinal_acceleration_t long_acc, curvature_t curv, CURVATURE_CALCULATION_MODE curv_calc, yaw_rate_t yaw_rate, int width)
                : heading(h), speed(s), driveDirection(drive_direction), vehicleLength(length), longitudinalAcceleration(long_acc), curvature(curv),
                curvatureCalculationMode(curv_calc), yawRate(yaw_rate), vehicleWidth(width) {}
    };

    class HighFrequencyContainer {

        private:
            // @attention: if ITS_STATION_TYPE is vehicle
            BasicVehicleContainerHighFrequency m_basicVehicleHF;
        
        public:
            HighFrequencyContainer(BasicVehicleContainerHighFrequency basic)
                : m_basicVehicleHF(basic) {}
    };

    class CamParameters {
        
        private:
            BasicContainer m_basicContainter;
            HighFrequencyContainer m_highFrequencyContainer;

        public:
            CamParameters(BasicContainer basic, HighFrequencyContainer containter)
                : m_basicContainter(basic), m_highFrequencyContainer(containter) {}
    };

    class CoopAwareness {

        private:
            int m_generationDeltaTime;
            CamParameters m_camParameters;

        public:
            CoopAwareness(int gnDeltaTime, CamParameters param) 
                : m_generationDeltaTime(gnDeltaTime), m_camParameters(param) {};
    };

}