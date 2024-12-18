import sys
import time
import json
from datetime import datetime

sys.path.append('/home/davidkopl/Documents/working_code_IoT/Python')

# Importy
from DFRobot_ADS1115 import ADS1115
from DFRobot_PH import DFRobot_PH
from DFRobot_EC import DFRobot_EC

# Inicializace senzorů
ads1115 = ADS1115()
ph_sensor = DFRobot_PH()
ec_sensor = DFRobot_EC()
ph_sensor.begin()
ec_sensor.begin()

# Soubor pro kalibraci
CALIBRATION_FILE = "calibration.json"

# Proměnné pro kalibraci
calibration_ph = False
calibration_ec = False
calibration_do = False

# Funkce pro uložení kalibrace pH
def save_calibration_ph(value):
    try:
        with open(CALIBRATION_FILE, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    data["ph"] = {"ph_7_voltage": value}

    with open(CALIBRATION_FILE, "w") as file:
        json.dump(data, file, indent=4)
    print("Kalibrační hodnota pH uložena:", value)

# Funkce pro kalibraci pH
def calibrate_ph():
    print("Spuštění kalibrace pH...")
    time.sleep(10)
    ads1115.setAddr_ADS1115(0x48)
    ads1115.setGain(0x00)
    adc_value = ads1115.readVoltage(1)['r']
    print(f"Kalibrační hodnota pH: {adc_value} mV")
    ph_sensor.calibration(adc_value)
    save_calibration_ph(adc_value)

# Funkce pro měření pH
def measure_ph(temperature=25):
    calibration_value = load_calibration_ph()
    if calibration_value is None:
        print("Kalibrace pH nebyla provedena.")
        return
    ads1115.setAddr_ADS1115(0x48)
    ads1115.setGain(0x00)
    adc_value = ads1115.readVoltage(1)['r']
    pH = ph_sensor.readPH(adc_value, temperature)
    print(f"Naměřená hodnota pH: {pH:.2f}")
    return pH

# Funkce pro uložení kalibrace EC
def save_calibration_ec(voltage, standard_ec):
    try:
        with open(CALIBRATION_FILE, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    data["ec"] = {
        "calibration_voltage": voltage,
        "standard_ec": standard_ec
    }

    with open(CALIBRATION_FILE, "w") as file:
        json.dump(data, file, indent=4)
    print("Kalibrace EC uložena:", data["ec"])

# Funkce pro kalibraci EC
def calibrate_ec():
    print("Spuštění kalibrace EC...")
    ads1115.setAddr_ADS1115(0x48)
    ads1115.setGain(0x00)
    adc_value = ads1115.readVoltage(0)['r']
    print(f"Naměřené napětí pro EC: {adc_value} V")
    standard_ec = float(input("Zadejte hodnotu standardního roztoku EC (v ms/cm): "))
    ec_sensor.calibration(adc_value, standard_ec)
    save_calibration_ec(adc_value, standard_ec)

# Funkce pro měření EC
def measure_ec():
    ads1115.setAddr_ADS1115(0x48)
    ads1115.setGain(0x00)
    adc_value = ads1115.readVoltage(0)['r']
    ec_value = ec_sensor.readEC(adc_value, 25)
    print(f"Naměřená hodnota EC: {ec_value:.4f} ms/cm")

# Funkce pro kalibraci DO
def calibrate_do():
    print("Spuštění kalibrace DO...")
    temp_c = float(input("Zadejte aktuální teplotu (°C): "))
    voltage_mv = read_adc_voltage(2)
    if voltage_mv:
        global CAL1_V, CAL1_T
        CAL1_V = voltage_mv
        CAL1_T = temp_c
        save_calibration()  # Uložení nové kalibrace
        print(f"Kalibrace DO dokončena: CAL1_V = {CAL1_V} mV, CAL1_T = {CAL1_T} °C")
    else:
        print("Nepodařilo se načíst napětí z ADC. Zkuste znovu.")

# Funkce pro měření DO
def measure_do():
    voltage_mv = read_adc_voltage(2)
    if not voltage_mv:
        print("Nepodařilo se načíst napětí z ADC. Kontrola senzoru.")
        time.sleep(2)
        return
    temperature_c = 25
    do_value = calculate_do(voltage_mv, temperature_c)
    print(f"DO: {do_value} ug/L")

# Hlavní smyčka
if __name__ == "__main__":
    while True:
        if calibration_ph:
            calibrate_ph()
            calibration_ph = False

        if calibration_ec:
            calibrate_ec()
            calibration_ec = False

        if calibration_do:
            calibrate_do()
            calibration_do = False

        measure_ph()
        measure_ec()
        measure_do()
        
        time.sleep(10)  # Pauza mezi měřeními
