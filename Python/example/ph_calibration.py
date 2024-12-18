import sys
import time
import json
sys.path.append('/home/davidkopl/Documents/working_code_IoT/Python')

from DFRobot_ADS1115 import ADS1115
from DFRobot_PH      import DFRobot_PH

# Inicializace senzorů
ads1115 = ADS1115()
ph = DFRobot_PH()

ph.begin()

# Soubor pro uložení kalibrace
CALIBRATION_FILE = "calibration.json"

def save_calibration_ph(value):
    """ Uložení kalibrační hodnoty pH do JSON souboru. """
    try:
        # Načtení existujícího obsahu
        with open(CALIBRATION_FILE, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    # Aktualizace sekce pro pH
    data["ph"] = {"ph_7_voltage": value}

    # Uložení zpět do souboru
    with open(CALIBRATION_FILE, "w") as file:
        json.dump(data, file, indent=4)
    print("Kalibrační hodnota pH uložena:", value)

def load_calibration_ph():
    """ Načtení kalibrační hodnoty pH ze JSON souboru. """
    try:
        with open(CALIBRATION_FILE, "r") as file:
            data = json.load(file)
            return data.get("ph", {}).get("ph_7_voltage", None)
    except FileNotFoundError:
        print("Kalibrační soubor neexistuje.")
        return None

# Kalibrace senzoru
def calibrate_ph():
    """ Funkce pro kalibraci pH senzoru. """
    print("Spuštění kalibrace... Umístěte senzor do pH 7.0 roztoku.")
    time.sleep(10)  # Čekání na stabilizaci senzoru
    
    # Čtení hodnoty z ADC
    ads1115.setAddr_ADS1115(0x48)
    ads1115.setGain(0x00)  # 6.144V rozsah
    adc_value = ads1115.readVoltage(1)['r']  # Měření na kanálu 1

    print(f"Kalibrační hodnota ADC: {adc_value} mV")
    ph.calibration(adc_value)  # Kalibrace pomocí knihovny
    save_calibration_ph(adc_value)  # Uložení kalibrační hodnoty

# Použití senzoru
def measure_ph(temperature=25):
    """ Měření pH pomocí senzoru s použitím kalibrační hodnoty. """
    calibration_value = load_calibration_ph()
    if calibration_value is None:
        print("Kalibrace nebyla provedena! Nejprve spusťte kalibraci.")
        return

    ads1115.setAddr_ADS1115(0x48)
    ads1115.setGain(0x00)
    adc_value = ads1115.readVoltage(1)['r']

    # Výpočet pH
    pH = ph.readPH(adc_value, temperature)
    print(f"Naměřená hodnota pH: {pH:.2f}")
    return pH

# Hlavní smyčka
if __name__ == "__main__":
    while True:
        action = input("Zvolte akci (c = kalibrace, m = měření pH, q = konec): ").strip().lower()
        if action == "c":
            calibrate_ph()
        elif action == "m":
            measure_ph()
        elif action == "q":
            print("Ukončuji program.")
            break
        else:
            print("Neznámá volba, zkuste to znovu.")
