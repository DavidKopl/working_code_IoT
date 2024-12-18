from collections import deque
import network
import os
import sys
import RPi.GPIO as GPIO
import time
import subprocess
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
#SERVER_URL = "https://aquaponicsui.onrender.com"#Bude nahrazeno ip-adresou serveru || http://192.168.0.69:3001
SERVER_URL = "http://192.168.0.69:3001"
last_temperature = 25
last_humidity = 50
CAL1_V = 108.48  # Kalibrační napětí v mV
CAL1_T = 23   # Kalibrační teplota
def fetch_config(server_url):
    try:
        response = requests.get(f"{server_url}/config")
        response.raise_for_status()
        config = response.json()
        # print("Config fetched:", config)
        return config
    except Exception as e:
        print(f"Failed to fetch config: {e}")
        return None
    
config = fetch_config(SERVER_URL)

def load_config(config=None):
    return {
        "wifi_ssid": config.get("wifi_ssid", "TP-Link_F7DA") if config else "TP-Link_F7DA",
        "wifi_password": config.get("wifi_password", "84403315") if config else "84403315",
        "timesleep": config.get("timesleep", 60) if config else 60,
        "dht_pin": config.get("dht_pin", 4) if config else 4,
        "config_update_time": config.get("config_update_time", 600) if config else 600,
        "relay_pins": config.get("relay_pins", [10, 17, 27, 22]) if config else [10, 17, 27, 22],
        "adc_threshold": config.get("adc_threshold", 10) if config else 10,
        "temp_hum_err": config.get("temp_hum_err", False) if config else False,
        "EC_err": config.get("ec_err", False) if config else False,
        "Ph_err": config.get("ph_err", False) if config else False,
        "DO_err": config.get("do_err", False) if config else False,
        "ONE_POINT_CALIBRATION": config.get("one_point_calibration", True) if config else True,
        "doCalibration": config.get("doCalibration", False) if config else False,
        "phCalibration": config.get("phCalibration", False) if config else False,
        "ecCalibration": config.get("ecCalibration", False) if config else False,
          "last_temperature": config.get("last_temperature", 25) if config else 25,
        "last_humidity": config.get("last_humidity", 50) if config else 50,
        "CAL1_V": config.get("cal1_v", 195) if config else 195,#smazat
        "CAL1_T": config.get("cal1_t", 25) if config else 25,#smazat
        "DO_Table": config.get(
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
        ],
        "maxHumidity": config.get("max_humidity", 90) if config else 90,
        "maxHumidityGap": config.get("max_humidity_gap", 10) if config else 10,
        "maxTemperature": config.get("max_temperature", 30) if config else 30,
        "maxTemperatureGap": config.get("max_temperature_gap", 10) if config else 10,
        "minTemperature": config.get("min_temperature", 15) if config else 15,
        "minTemperatureGap": config.get("min_temperature_gap", 10) if config else 10,
        "minCO": config.get("min_co", 600) if config else 600,
        "minCOGap": config.get("min_co_gap", 200) if config else 200,
        "target_vpd": config.get("target_vpd", 1.2) if config else 1.2,
        "co2_min": config.get("co2_min", 600) if config else 600,#Mozne smazat
        "co2_max": config.get("co2_max", 800) if config else 800, #Mozne smazat
        "temp_min": config.get("temp_min", 15) if config else 15,
        "temp_max": config.get("temp_max", 30) if config else 30,
        "humidity_min": config.get("humidity_min", 50) if config else 50,
        "humidity_max": config.get("humidity_max", 90) if config else 90,
    }
 
# Použití
config_data = load_config(config)

def check_wifi_connection():
    """Funkce pro kontrolu, zda je Wi-Fi připojena."""
    try:
        # Kontrola, zda je zařízení připojeno k nějaké síti
        result = subprocess.run(["nmcli", "-t", "-f", "ACTIVE,SSID", "dev", "wifi"], capture_output=True, text=True)
        
        # Rozdělení výstupu na řádky
        lines = result.stdout.splitlines()
        
        # Kontrola, zda je některý řádek s 'yes' ve sloupci ACTIVE
        for line in lines:
            if line.startswith('yes'):
                return True  # Pokud je 'yes', znamená to připojení
        
        # Pokud není žádný 'yes', není připojeno
        return False
        
    except subprocess.CalledProcessError as e:
        print(f"Chyba při kontrole Wi-Fi připojení: {e}")
        return False

def connect_to_wifi(ssid, password):
    try:
        # Spustíme příkaz pro připojení k Wi-Fi
        subprocess.run(["nmcli", "dev", "wifi", "connect", ssid, "password", password], check=True)
        print(f"Connected to {ssid}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to connect to {ssid}: {e}")

    # Try connecting to the preferred Wi-Fi
connect_to_wifi(config_data["wifi_ssid"], config_data["wifi_password"])

def relay_setup():
    GPIO.setmode(GPIO.BCM)  # Použití číslování GPIO pinů
    GPIO.setwarnings(False)  # Vypnutí varování
    print("Hello there: ")
    print(config_data)
    # Nastavení pinů jako výstupy
    for pin in config_data["relay_pins"]:
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

CALIBRATION_FILE = "calibration.json"  # Název souboru s kalibrací
def load_calibration():
    """ Načtení kalibračních hodnot z JSON souboru """
    global CAL1_V, CAL1_T
    try:
        with open(CALIBRATION_FILE, "r") as file:
            data = json.load(file)
            if "DO" in data:
                CAL1_V = data["DO"].get("voltage", CAL1_V)
                CAL1_T = data["DO"].get("temperature", CAL1_T)
                # print(f"Načtení kalibrace: CAL1_V = {CAL1_V} mV, CAL1_T = {CAL1_T} °C")
            else:
                print("Sekce 'DO' nenalezena v kalibračním souboru. Používají se výchozí hodnoty.")
    except FileNotFoundError:
        print("Kalibrační soubor nenalezen. Používají se výchozí hodnoty.")
    except json.JSONDecodeError:
        print("Chyba při čtení kalibračního souboru. Používají se výchozí hodnoty.")

def save_calibration():
    """ Uložení aktuálních kalibračních hodnot DO do JSON souboru (přepisování pouze DO) """
    try:
        # Načtení existujícího souboru pro zachování ostatních dat
        with open(CALIBRATION_FILE, "r") as file:
            data = json.load(file)
        
        # Uložení nových hodnot DO
        data["DO"] = {
            "voltage": CAL1_V,
            "temperature": CAL1_T
        }

        # Uložení zpět do souboru
        with open(CALIBRATION_FILE, "w") as file:
            json.dump(data, file, indent=4)
        print(f"Kalibrace DO uložena: CAL1_V = {CAL1_V} mV, CAL1_T = {CAL1_T} °C")
    
    except FileNotFoundError:
        print("Kalibrační soubor nenalezen. Vytvářím nový.")
        # Pokud soubor neexistuje, vytvořte nový soubor
        data = {
            "DO": {
                "voltage": CAL1_V,
                "temperature": CAL1_T
            }
        }
        with open(CALIBRATION_FILE, "w") as file:
            json.dump(data, file, indent=4)
        print(f"Kalibrace DO uložena (nový soubor): CAL1_V = {CAL1_V} mV, CAL1_T = {CAL1_T} °C")

def calibrate_do(voltage_mv, temp_c):
    """ Kalibrační procedura DO senzoru """
    print("=== Kalibrace DO senzoru ===")
    if voltage_mv:
        global CAL1_V, CAL1_T
        CAL1_V = voltage_mv
        CAL1_T = temp_c
        save_calibration()  # Uložení nové kalibrace
        print(f"Kalibrace dokončena: CAL1_V = {CAL1_V} mV, CAL1_T = {CAL1_T} °C")
    else:
        print("Nepodařilo se načíst napětí z ADC. Zkuste znovu.")

def read_do(voltage_mv, temperature_c):
    """ Výpočet hodnoty rozpuštěného kyslíku (DO) """
    try:
        # Kontrola vstupních hodnot
        if CAL1_V is None or temperature_c is None or CAL1_T is None:
            print(CAL1_T, CAL1_V, temperature_c)
            raise ValueError("Neplatné hodnoty kalibrace nebo teploty.")

        temp_index = int(temperature_c)
        if temp_index < 0 or temp_index >= len(config_data["DO_Table"]):
            raise ValueError("Teplota mimo rozsah DO tabulky.")
        
        v_saturation = CAL1_V + 35 * temperature_c - CAL1_T * 35
        if v_saturation == 0:
            raise ZeroDivisionError("Hodnota v_saturation je nulová.")
        
        do_value = voltage_mv * config_data["DO_Table"][temp_index] / v_saturation
        return round(do_value, 2)
    except ValueError as e:
        print(f"Chyba při výpočtu DO: {e}")
        return None
    except ZeroDivisionError as e:
        print(f"Chyba při výpočtu DO (dělení nulou): {e}")
        return None


# def read_do(voltage_mv, temperature_c):
#     temperature_index = int(temperature_c)
#     if temperature_index < 0 or temperature_index >= len(config_data["DO_Table"]):
#         raise ValueError("Temperature index out of range for DO_Table")
    
#     if config_data["ONE_POINT_CALIBRATION"]:
#         v_saturation = config_data["CAL1_V"] + 35 * temperature_c - config_data["CAL1_T"] * 35
#         return (voltage_mv * config_data["DO_Table"][temperature_index] // v_saturation)
def calibrate_ph_sensor(ads1115, ph, temperature=25):
    try:
        ads1115.setAddr_ADS1115(0x48)
        ads1115.setGain(ADS1115_REG_CONFIG_PGA_6_144V)
        # Čtení napětí z ADC kanálu 1
        adc0 = ads1115.readVoltage(1)
        print(f"A0: {adc0['r']} mV")
        # Kalibrace pH senzoru
        ph.calibration(adc0['r'])
        # Pauza pro stabilizaci
        time.sleep(1.0)
        
    except Exception as e:
        print(f"Chyba při kalibraci pH senzoru: {e}")

def calibrate_ec(adc, ec, temperature=25):
    try:
        # ads1115.setAddr_ADS1115(0x48)
        # ads1115.setGain(ADS1115_REG_CONFIG_PGA_6_144V)
        # adc0 = ads1115.readVoltage(0)
        if adc is None:
            # print(adc)
            raise ValueError("Nepodařilo se přečíst hodnotu z ADS1115.")

        print(f"A0: {adc} mV")  # Zobrazení hodnoty v mV
        ec.calibration(adc, temperature)
        # print(f"EC senzor byl úspěšně kalibrován na hodnotu {adc0['r']} mV při teplotě {temperature}°C.")
    except Exception as e:
        print(f"Chyba při měření nebo kalibraci EC: {e}")


last_config_update = time.time()  # Čas posledního načtení konfigurace 
wifi_connected = False  # Zde uchováváme stav připojení




























while True:
    current_time = time.time()
       # Kontrola připojení k Wi-Fi pouze každých 10 sekund (nebo jiný interval)
    wifi_connected = check_wifi_connection()
    load_calibration()

    if wifi_connected:
        print("Wi-Fi is active")
    else:
        print("Wi-Fi není připojeno, pokusím se připojit...")
        connect_to_wifi(config_data["wifi_ssid"], config_data["wifi_password"])
        
    print(last_config_update, " - ",current_time, " = ",current_time-last_config_update)
    # Každou minutu načíst konfiguraci
    if current_time - last_config_update >= config_data["config_update_time"]:
        config = fetch_config(SERVER_URL)
        if config:
            config_data = load_config(config)
            print(config_data["doCalibration"], config_data["phCalibration"], config_data["ecCalibration"])
        last_config_update = current_time

    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, config_data["dht_pin"])
    
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
    try:
        do_value = read_do(voltage_mv, last_temperature if last_temperature else 25)
        print(do_value, voltage_mv, last_temperature, temperature)
        PH = ph.readPH(adc1, last_temperature)
        EC = ec.readEC(adc0, last_temperature if last_temperature else 25)
    except ValueError as ve:
        print(f"Chyba při výpočtu DO,pH nebo EC zde: {ve}")


    try:
        co2_data = mh_z19.read_from_pwm()
        co2_value = co2_data.get("co2", None)
        
    except Exception as e:
        co2_value = None
#Kalibrace
    if config_data["phCalibration"]:
        calibrate_ph_sensor(ads1115,ph, last_temperature)
    if config_data["doCalibration"]:
        calibrate_do(voltage_mv,last_temperature)
    if config_data["ecCalibration"]:
        calibrate_ec(adc0,ec,last_temperature)

 # Logika pro zapnutí/vypnutí relé
    if last_humidity >= config_data["maxHumidity"]:
        relay_on(config_data["relay_pins"][0])
    elif(last_humidity <= config_data["maxHumidity"] - config_data["maxHumidityGap"]):
        relay_off(config_data["relay_pins"][0]) 

    if last_temperature > config_data["maxTemperature"]:
        relay_on(config_data["relay_pins"][1])  
    elif(last_temperature <= config_data["maxTemperature"] - config_data["maxTemperatureGap"]):
        relay_off(config_data["relay_pins"][1])  

    if last_temperature < config_data["minTemperature"]:
        relay_on(config_data["relay_pins"][2])
    elif(last_temperature >= config_data["minTemperature"] + config_data["minTemperatureGap"]):
        relay_off(config_data["relay_pins"][2]) 

    if co2_value is not None and co2_value <= config_data["minCO"]:
        relay_on(config_data["relay_pins"][3]) 
    elif co2_value is not None and co2_value >= config_data["minCO"] + config_data["minCOGap"]:
        relay_off(config_data["relay_pins"][3])  

    # Sestavení dat pro odeslání

    print(do_value)#Tady mam jeste data o do
    print(co2_value)
    data = {
        "sensor_id": "device_1",
        "temperature": round(last_temperature,2),
        "humidity": round(last_humidity,2),
        "target_vpd": config_data["target_vpd"],
        "co2": co2_value if co2_value else None, 
        "ec": EC,
        "ph": PH,
        "do_value": do_value,
        "adc_readings": {"adc0_EC": adc0, "adc1_Ph": adc1, "adc2_DO": adc2},
        "relays": {
            "relay1_hum_minus": GPIO.input(config_data["relay_pins"][0]) == GPIO.LOW,
            "relay2_temp_minus": GPIO.input(config_data["relay_pins"][1]) == GPIO.LOW,
            "relay3_temp_plus": GPIO.input(config_data["relay_pins"][2]) == GPIO.LOW,
            "relay4_co2_plus": GPIO.input(config_data["relay_pins"][3]) == GPIO.LOW,
        },
        
        "errors": {"temp_hum_err":temp_hum_err}
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
    time.sleep(config_data["timesleep"])
