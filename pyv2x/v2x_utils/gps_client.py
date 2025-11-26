import serial
from os import path
import pynmea2


class NMEAdata:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return "\n".join([ f"{key}: {val}" for key, val in self.__dict__.items() ])

class RMC(NMEAdata):
    pass

class VTG(NMEAdata):
    pass

class GGA(NMEAdata):
    pass

class GSV(NMEAdata):
    pass

class GSA(NMEAdata):
    pass



class GPSclient:

    _file = "/dev/ttyACM0"
    _baudrate = 9600
    _serial_conn = serial.Serial(_file, _baudrate, timeout=1)

    @classmethod
    def new(cls, file: str, baud: int) -> "GPSclient":
        if not path.exists(file):
            raise Exception(f"file {file} not found")
        
        cls._baudrate, cls._file = baud, file
        
        
        return cls()

    @classmethod
    def get_data(cls, t: str = "RMC"):

        
        if cls._serial_conn.is_open:
            try:
                line = cls._serial_conn.readline().decode('ascii', errors='replace').strip()
                
                if line.startswith('$'):
                    try:
                        msg = pynmea2.parse(line)
                        
                        match msg.sentence_type:
                            
                            case "RMC":
                                try:
                                    knots = float(msg.spd_over_grnd)
                                    kmh = knots * 1.852
                                except (ValueError, TypeError):
                                    kmh = 0.0
                                    
                                return RMC(
                                    timestamp=msg.timestamp,                # hhmmss.ss (UTC Time)
                                    status=msg.status,                      # 'A'=Dati validi, 'V'=Non validi
                                    lat=msg.lat,                            # DDMM.MMMMM (Gradi e Minuti)
                                    latitude=msg.latitude,                  # decimal degrees
                                    lat_dir=msg.lat_dir,                    # 'N' o 'S' (quale emisfero)
                                    lon=msg.lon,                            # DDDMM.MMMMM (Gradi e Minuti)
                                    longitude=msg.longitude,                # decimal degrees
                                    lon_dir=msg.lon_dir,                    # 'E' o 'W' (quale emisfero)
                                    speedKnots=msg.spd_over_grnd,           # Nodi (Knots) - Moltiplica per 1.852 per km/h
                                    speedKmh=kmh,                           # cast a manina
                                    heading=msg.true_course,                # Gradi (°) - Rotta Vera (movimento) - rispetto a nord geografico
                                    date=msg.datestamp,                     # DDMMYY (Data)
                                    magnetic_variation=msg.mag_variation,   # Gradi (°) - Declinazione magnetica - diff tra nord vero e nord magnetico
                                    mag_var_dir=msg.mag_var_dir             # 'E' o 'W'
                                )

                            case "GGA":
                                return GGA(
                                    time=msg.timestamp,                     # hhmmss.ss (UTC Time)
                                    latitude=msg.lat,                       # DDMM.MMMMM
                                    lat_dir=msg.lat_dir,                    # 'N' o 'S'
                                    longitude=msg.lon,                      # DDDMM.MMMMM
                                    lon_dir=msg.lon_dir,                    # 'E' o 'W'
                                    fix_quality=msg.gps_qual,               # 0=Invalid, 1=GPS (STD), 2=DGPS, 4=RTK (qualita del segnale in ordine crescente)
                                    num_satellites=msg.num_sats,            # Intero (Satelliti usati per il calcolo)
                                    hdop=msg.horizontal_dil,                # Adimensionale (Precisione Orizzontale, <1 è ottimo)
                                    altitude=msg.altitude,                  # Metri (M) - Altezza sul livello del mare
                                    altitude_units=msg.altitude_units,      # 'M'
                                    geoid_height=msg.geo_sep,               # Metri (M) - Differenza Geoide/Ellissoide
                                    geoid_height_units=msg.geo_sep_units    # 'M'
                                )
                            

                            case "VTG":
                                return VTG(
                                    true_track=msg.true_track,              # Gradi (°) - Rotta rispetto al Nord vero
                                    magnetic_track=msg.mag_track,           # Gradi (°) - Rotta rispetto al Nord magnetico
                                    speed_knots=msg.spd_over_grnd_kts,      # Nodi
                                    speed_kmh=msg.spd_over_grnd_kmh         # Km/h
                                )

                            case "GSA": # per sapere quanto è affidabile il calcolo del gps
                                return GSA(
                                    mode=msg.mode,                          # 'M'=Manuale, 'A'=Automatico
                                    fix_type=msg.mode_fix_type,             # 1=No Fix, 2=2D, 3=3D

                                    # Lista degli ID dei satelliti usati (fino a 12)
                                    sat_ids=[
                                        msg.sv_id01, msg.sv_id02, msg.sv_id03, msg.sv_id04,
                                        msg.sv_id05, msg.sv_id06, msg.sv_id07, msg.sv_id08,
                                        msg.sv_id09, msg.sv_id10, msg.sv_id11, msg.sv_id12
                                    ],
                                    pdop=msg.pdop,                          # Adimensionale (Precisione Posizione)
                                    hdop=msg.hdop,                          # Adimensionale (Precisione Orizzontale)
                                    vdop=msg.vdop                           # Adimensionale (Precisione Verticale)
                                )

                            case "GSV":
                                return GSV(
                                    num_messages=msg.num_messages,          # Intero (Totale messaggi nel ciclo)
                                    msg_num=msg.msg_num,                    # Intero (Indice messaggio corrente)
                                    num_sv_in_view=msg.num_sv_in_view,      # Intero (Satelliti totali in vista)
                                    
                                    # Blocco Satellite 1
                                    sv_prn_1=msg.sv_prn_num_1,              # ID Satellite
                                    elevation_1=msg.elevation_deg_1,        # Gradi (°)
                                    azimuth_1=msg.azimuth_1,                # Gradi (°)
                                    snr_1=msg.snr_1,                        # dBHz (Signal-to-Noise Ratio)
                                    
                                    # Blocco Satellite 2 (potrebbe essere vuoto)
                                    sv_prn_2=msg.sv_prn_num_2,              # ID Satellite
                                    elevation_2=msg.elevation_deg_2,        # Gradi (°)
                                    azimuth_2=msg.azimuth_2,                # Gradi (°)
                                    snr_2=msg.snr_2,                        # dBHz
                                    
                                    # Blocco Satellite 3 (potrebbe essere vuoto)
                                    sv_prn_3=msg.sv_prn_num_3,              # ID Satellite
                                    elevation_3=msg.elevation_deg_3,        # Gradi (°)
                                    azimuth_3=msg.azimuth_3,                # Gradi (°)
                                    snr_3=msg.snr_3,                        # dBHz
                                    
                                    # Blocco Satellite 4 (potrebbe essere vuoto)
                                    sv_prn_4=msg.sv_prn_num_4,              # ID Satellite
                                    elevation_4=msg.elevation_deg_4,        # Gradi (°)
                                    azimuth_4=msg.azimuth_4,                # Gradi (°)
                                    snr_4=msg.snr_4                         # dBHz
                                )

                    except pynmea2.ParseError:
                        return None
                        
            except Exception as e:
                if not cls._serial_conn.is_open:
                    return None


