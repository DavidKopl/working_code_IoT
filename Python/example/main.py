from collections import deque
import sys
import RPi.GPIO as GPIO
import time
import requests
import json
import mh_z19
import Adafruit_DHT
sys.path.append('/home/davidkopl/Documents/working_code_IoT/Python')
from DFRobot_ADS1115 import ADS1115
from DFRobot_EC      import DFRobot_EC
from DFRobot_PH      import DFRobot_PH
# Konstanty
ADS1115_REG_CONFIG_PGA_6_144V        = 0x00 # 6.144V range = Gain 2/3
ADS1115_REG_CONFIG_PGA_4_096V        = 0x02 # 4.096V range = Gain 1
ADS1115_REG_CONFIG_PGA_2_048V        = 0x04 # 2.048V range = Gain 2 (default)
ADS1115_REG_CONFIG_PGA_1_024V        = 0x06 # 1.024V range = Gain 4
ADS1115_REG_CONFIG_PGA_0_512V        = 0x08 # 0.512V range = Gain 8
ADS1115_REG_CONFIG_PGA_0_256V        = 0x0A # 0.256V range = Gain 16
VREF = 5000  # Referenční napětí v mV
ADC_RES = 32768
DHT_SENSOR = Adafruit_DHT.DHT22
SERVER_URL = "http://192.168.0.69:3000"#Bude nahrazeno ip-adresou serveru

def fetch_config(server_url):
    try:
        response = requests.get(f"{server_url}/config")
        response.raise_for_status()
        config = response.json()
        print("Config fetched:", config)
        return config
    except Exception as e:
        print(f"Failed to fetch config: {e}")
        return None
    
config = fetch_config(SERVER_URL)

DHT_PIN = config.get("dht_pin", 4) if config else 4
config_update_time = config.get("config_update_time", 600) if config else 600
relay_pins = config.get("relay_pins", [10, 17, 27, 22]) if config else [10, 17, 27, 22]
adc_threshold = config.get("adc_threshold", 10) if config else 10
last_temperature = config.get("last_temperature", 25) if config else 25
last_humidity = config.get("last_humidity", 50) if config else 50
temp_hum_err = config.get("temp_hum_err", False) if config else False
EC_err = config.get("ec_err", False) if config else False
Ph_err = config.get("ph_err", False) if config else False
DO_err = config.get("do_err", False) if config else False
ONE_POINT_CALIBRATION = config.get("one_point_calibration", True) if config else True
CAL1_V = config.get("cal1_v", 195) if config else 195
CAL1_T = config.get("cal1_t", 25) if config else 25

DO_Table = config.get(
    "do_table",
    [
        14460, 14220, 13820, 13440, 13090, 12740, 12420, 12110, 11810, 11530,
        11260, 11010, 10770, 10530, 10300, 10080, 9860, 9660, 9460, 9270,
        9080, 8900, 8730, 8570, 8410, 8250, 8110, 7960, 7820, 7690,
        7560, 7430, 7300, 7180, 7070, 6950, 6840, 6730, 6630, 6530, 6410,
    ],
) if config else [
    14460, 14220, 13820, 13440, 13090, 12740, 12420, 12110, 11810, 11530,
    11260, 11010, 10770, 10530, 10300, 10080, 9860, 9660, 9460, 9270,
    9080, 8900, 8730, 8570, 8410, 8250, 8110, 7960, 7820, 7690,
    7560, 7430, 7300, 7180, 7070, 6950, 6840, 6730, 6630, 6530, 6410,
]

maxHumidity = config.get("max_humidity", 90) if config else 90
maxHumidityGap = config.get("max_humidity_gap", 10) if config else 10
maxTemperature = config.get("max_temperature", 30) if config else 30
maxTemperatureGap = config.get("max_temperature_gap", 10) if config else 10
minTemperature = config.get("min_temperature", 15) if config else 15
minTemperatureGap = config.get("min_temperature_gap", 10) if config else 10
minCO = config.get("min_co", 600) if config else 600
minCOGap = config.get("min_co_gap", 200) if config else 200

target_vpd = config.get("target_vpd", 1.2) if config else 1.2
co2_min = config.get("co2_min", 600) if config else 600
co2_max = config.get("co2_max", 800) if config else 800
temp_min = config.get("temp_min", 15) if config else 15
temp_max = config.get("temp_max", 30) if config else 30
humidity_min = config.get("humidity_min", 50) if config else 50
humidity_max = config.get("humidity_max", 90) if config else 90





# DHT_PIN = 4
# adc_threshold = 10
# relay_pins = [10,17,27,22] 

# # Výchozí hodnoty (první iterace)
# last_temperature = 25.0  # Výchozí teplota, např. pokojová teplota
# last_humidity = 50.0     # Výchozí vlhkost, např. typická hodnota
# temp_hum_err = False
# EC_err = False
# Ph_err = False
# DO_err = False
# target_vpd = 1.2  # kPa

# Kalibrace DO
# CAL1_V = 195
# CAL1_T = 25
# DO_Table = [
#     14460, 14220, 13820, 13440, 13090, 12740, 12420, 12110, 11810, 11530,
#     11260, 11010, 10770, 10530, 10300, 10080, 9860, 9660, 9460, 9270,
#     9080, 8900, 8730, 8570, 8410, 8250, 8110, 7960, 7820, 7690,
#     7560, 7430, 7300, 7180, 7070, 6950, 6840, 6730, 6630, 6530, 6410
# ]
def relay_setup():
    GPIO.setmode(GPIO.BCM)  # Použití číslování GPIO pinů
    GPIO.setwarnings(False)  # Vypnutí varování
    # Nastavení pinů jako výstupy
    for pin in relay_pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)  # Relé vypnuto (závisí na typu relé)
# Inicializace
ads1115 = ADS1115()
ec = DFRobot_EC()
ph = DFRobot_PH()
ec.begin()
ph.begin()
relay_setup()

def relay_on(pin):
    GPIO.output(pin, GPIO.LOW)  # Zapnutí relé (LOW u aktivního LOW relé)

def relay_off(pin):
    GPIO.output(pin, GPIO.HIGH)  # Vypnutí relé (HIGH u aktivního LOW relé)

# def cleanup():
#     GPIO.cleanup()  # Reset GPIO pinů do výchozího stavu


def read_do(voltage_mv, temperature_c):
    temperature_index = int(temperature_c)
    if temperature_index < 0 or temperature_index >= len(DO_Table):
        raise ValueError("Temperature index out of range for DO_Table")
    
    if ONE_POINT_CALIBRATION:
        v_saturation = CAL1_V + 35 * temperature_c - CAL1_T * 35
        return (voltage_mv * DO_Table[temperature_index] // v_saturation)


last_config_update = time.time()  # Čas posledního načtení konfigurace
while True:
    current_time = time.time()
    print(last_config_update, " - ",current_time, " = ",current_time-last_config_update)
    # Každou minutu načíst konfiguraci
    if current_time - last_config_update >= config_update_time:
        config = fetch_config(SERVER_URL)
        if config:
            target_vpd = config.get("target_vpd", target_vpd)
            co2_min = config.get("co2_min", co2_min)
            co2_max = config.get("co2_max", co2_max)
            temp_min = config.get("temp_min", temp_min)
            temp_max = config.get("temp_max", temp_max)
            humidity_min = config.get("humidity_min", humidity_min)
            humidity_max = config.get("humidity_max", humidity_max)
        last_config_update = current_time
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    
    # Aktualizace posledních známých hodnot, pokud jsou data platná + info o erroru.
    if temperature and humidity is not None:
        last_temperature = temperature
        last_humidity = humidity
        temp_hum_err = False
    else: 
        temp_hum_err = True

    try:
        # Nastavení zisku a čtení hodnoty z ADS1115
        ads1115.setGain(ADS1115_REG_CONFIG_PGA_6_144V)
        adc0 = ads1115.readVoltage(0)['r']
        adc1 = ads1115.readVoltage(1)['r']
        adc2 = ads1115.readVoltage(2)['r']
        voltage_mv = VREF * adc2 // ADC_RES
    except OSError as e:
        print(f"Chyba při komunikaci s ADS1115: {e}")
        adc0, adc1, adc2, voltage_mv = None, None, None, None  # Nastavení hodnot na None při chybě
    
    

    # Kontrola senzorů a výpočty
    EC, PH, do_value = None, None, None
    if adc0 and adc0 > adc_threshold:
        EC = ec.readEC(adc0, last_temperature if last_temperature else 25)
        EC_err = False
    elif(adc0 == None or adc0 < 5):
        print("EC senzor nepripojen nebo chyba ADC")
        EC_err = False
    else:
        EC_err = True

    if adc1 and (2200 > adc1 > 600):
        PH = ph.readPH(adc1, last_temperature)
        Ph_err = False
    elif(adc1 == None or adc1 >2700):
        print("PH senzor nepripojen nebo chyba ADC")
        Ph_err = False
    else:
        Ph_err = True

    if adc2 and adc2 > adc_threshold:
        try:
            do_value = read_do(voltage_mv, last_temperature if last_temperature else 25)
            DO_err = False
        except ValueError as ve:
            print(f"Chyba při výpočtu DO: {ve}")
            DO_err = True
    else:
        print("DO senzor nepripojen nebo chyba ADC")
        DO_err = False

    try:
        co2_data = mh_z19.read_from_pwm()
        co2_value = co2_data.get("co2", None)
    except Exception as e:
        print(f"CO2 read failed: {e}")
        co2_value = {"co2": None}
    # Sestavení dat pro odeslání

 # Logika pro zapnutí/vypnutí relé
    if last_humidity >= maxHumidity:
        relay_on(relay_pins[0])
    elif(last_humidity <= maxHumidity - maxHumidityGap):
        relay_off(relay_pins[0]) 

    if last_temperature > maxTemperature:
        relay_on(relay_pins[1])  
    elif(last_temperature <= maxTemperature - maxTemperatureGap):
        relay_off(relay_pins[1])  

    if last_temperature < minTemperature:
        relay_on(relay_pins[2])
    elif(last_temperature >= minTemperature + minTemperatureGap):
        relay_off(relay_pins[2]) 

    if co2_value is not None and co2_value <= minCO:
        relay_on(relay_pins[3]) 
    elif(co2_value >= minCO + minCOGap):
        relay_off(relay_pins[3])  

    # Sestavení dat pro odeslání
    data = {
        "sensor_id": "device_1",
        "temperature": round(last_temperature,2),
        "humidity": round(last_humidity,2),
        "target_vpd": target_vpd,
        "co2": co2_value if co2_value else None, 
        "ec": EC,
        "ph": PH,
        "do": do_value,
        "adc_readings": {"adc0_EC": adc0, "adc1_Ph": adc1, "adc2_DO": adc2},
        "relays": {
            "relay1_hum_minus": GPIO.input(relay_pins[0]) == GPIO.LOW,
            "relay2_temp_minus": GPIO.input(relay_pins[1]) == GPIO.LOW,
            "relay3_temp_plus": GPIO.input(relay_pins[2]) == GPIO.LOW,
            "relay4_co2_plus": GPIO.input(relay_pins[3]) == GPIO.LOW,
        },
        
        "errors": {"temp_hum_err":temp_hum_err, "EC_error": EC_err, "Ph_error": Ph_err, "DO_error":DO_err}
    }

    # Odeslání dat na server
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(f"{SERVER_URL}/data", data=json.dumps(data), headers=headers)
        print(f"Server responded with status: \033[32m{response.status_code}\033[0m")
        print(f"\033[32m{response.text}\033[0m")

    except Exception as e:
        print(f"Failed to send data: {e}")

    # Zpoždění mezi iteracemi
    time.sleep(10)
