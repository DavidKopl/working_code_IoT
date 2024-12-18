import json
import time
import sys
sys.path.append('/home/davidkopl/Documents/working_code_IoT/Python')
from DFRobot_ADS1115 import ADS1115
from DFRobot_EC import DFRobot_EC
from DFRobot_PH import DFRobot_PH

# Konstanty pro ADC a kalibraci
ADS1115_REG_CONFIG_PGA_6_144V = 0x00  # Rozsah 6.144V
VREF = 5000  # Referenční napětí v mV
ADC_RES = 32768  # Rozlišení ADC
DEFAULT_TEMP = 25  # Výchozí teplota pro kalibraci

# DO Tabulka (hodnoty pro koncentrace rozpuštěného kyslíku)
DO_TABLE = [
    14460, 14220, 13820, 13440, 13090, 12740, 12420, 12110, 11810, 11530,
    11260, 11010, 10770, 10530, 10300, 10080, 9860, 9660, 9460, 9270,
    9080, 8900, 8730, 8570, 8410, 8250, 8110, 7960, 7820, 7690,
    7560, 7430, 7300, 7180, 7070, 6950, 6840, 6730, 6630, 6530, 6410
]

# Inicializace senzorů
ads1115 = ADS1115()
ec = DFRobot_EC()
ph = DFRobot_PH()
ec.begin()
ph.begin()

# Kalibrační nastavení
CALIBRATION_FILE = "calibration.json"  # Název souboru s kalibrací
CAL1_V = 108.48  # Kalibrační napětí v mV
CAL1_T = 23   # Kalibrační teplota


def calculate_do(voltage_mv, temperature_c):
    """ Výpočet hodnoty rozpuštěného kyslíku (DO) """
    try:
        temp_index = int(temperature_c)
        if temp_index < 0 or temp_index >= len(DO_TABLE):
            raise ValueError("Teplota mimo rozsah DO tabulky.")
        
        v_saturation = CAL1_V + 35 * temperature_c - CAL1_T * 35
        do_value = voltage_mv * DO_TABLE[temp_index] / v_saturation
        return round(do_value, 2)
    except ValueError as e:
        print(f"Chyba při výpočtu DO: {e}")
        return None


def read_adc_voltage(channel):
    """ Čtení napětí z ADC (ADS1115) """
    ads1115.setGain(ADS1115_REG_CONFIG_PGA_6_144V)
    try:
        adc_reading = ads1115.readVoltage(channel)
        if adc_reading and 'r' in adc_reading:
            voltage_mv = VREF * adc_reading['r'] / ADC_RES
            return voltage_mv
        else:
            print(f"Chyba při čtení ADC kanálu {channel}")
            return None
    except Exception as e:
        print(f"Chyba při čtení ADC: {e}")
        return None


def load_calibration():
    """ Načtení kalibračních hodnot z JSON souboru """
    global CAL1_V, CAL1_T
    try:
        with open(CALIBRATION_FILE, "r") as file:
            data = json.load(file)
            if "DO" in data:
                CAL1_V = data["DO"].get("voltage", CAL1_V)
                CAL1_T = data["DO"].get("temperature", CAL1_T)
                print(f"Načtení kalibrace: CAL1_V = {CAL1_V} mV, CAL1_T = {CAL1_T} °C")
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
        
def calibrate_do():
    """ Kalibrační procedura DO senzoru """
    print("=== Kalibrace DO senzoru ===")
    temp_c = float(input("Zadejte aktuální teplotu (°C): "))
    voltage_mv = read_adc_voltage(2)
    
    if voltage_mv:
        global CAL1_V, CAL1_T
        CAL1_V = voltage_mv
        CAL1_T = temp_c
        save_calibration()  # Uložení nové kalibrace
        print(f"Kalibrace dokončena: CAL1_V = {CAL1_V} mV, CAL1_T = {CAL1_T} °C")
    else:
        print("Nepodařilo se načíst napětí z ADC. Zkuste znovu.")


def main():
    """ Hlavní smyčka programu """
    print("=== Měření hodnoty DO ===")
    while True:
        try:
            # Čtení napětí z ADC
            voltage_mv = read_adc_voltage(2)
            if not voltage_mv:
                print("Nepodařilo se načíst napětí z ADC. Kontrola senzoru.")
                time.sleep(2)
                continue

            # Výpočet hodnoty DO
            temperature_c = DEFAULT_TEMP
            do_value = calculate_do(voltage_mv, temperature_c)

            # Výpis hodnot
            print(f"Napětí: {voltage_mv:.2f} mV | Teplota: {temperature_c} °C | DO: {do_value} ug/L DO: {round(do_value/1000,2)} mg/L")

            # Čekání mezi měřeními
            time.sleep(5)

        except KeyboardInterrupt:
            print("Program ukončen uživatelem.")
            break


if __name__ == "__main__":
    load_calibration()
    print("1: Kalibrace DO senzoru")
    print("2: Spustit měření DO")
    choice = input("Vyberte možnost (1/2): ")

    if choice == "1":
        calibrate_do()
    elif choice == "2":
        main()
    else:
        print("Neplatná volba. Ukončuji program.")
