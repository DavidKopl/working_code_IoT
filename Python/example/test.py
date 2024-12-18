import json
import time
from datetime import datetime

# Konstanty pro kalibraci a výpočet DO
DEFAULT_TEMP = 25  # Výchozí teplota
CALIBRATION_FILE = "calibrations.json"  # Soubor pro uložení kalibrací

# DO Tabulka pro výpočet hodnoty rozpuštěného kyslíku
DO_TABLE = [
    14460, 14220, 13820, 13440, 13090, 12740, 12420, 12110, 11810, 11530,
    11260, 11010, 10770, 10530, 10300, 10080, 9860, 9660, 9460, 9270,
    9080, 8900, 8730, 8570, 8410, 8250, 8110, 7960, 7820, 7690,
    7560, 7430, 7300, 7180, 7070, 6950, 6840, 6730, 6630, 6530, 6410
]

# Inicializace hodnot kalibrace
calibration_data = {
    "DO": {"voltage": 108.48, "temperature": 23},  # Výchozí kalibrace
}

def load_calibration(sensor_name):
    """Načtení kalibrace ze souboru."""
    try:
        with open(CALIBRATION_FILE, "r") as file:
            data = json.load(file)
            return data.get(sensor_name, {})
    except FileNotFoundError:
        print(f"Kalibrační soubor '{CALIBRATION_FILE}' nenalezen. Použijí se výchozí hodnoty.")
        return {}

def save_calibration(sensor_name, calibration):
    """Uložení kalibrace do souboru."""
    try:
        with open(CALIBRATION_FILE, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}

    data[sensor_name] = calibration

    with open(CALIBRATION_FILE, "w") as file:
        json.dump(data, file, indent=4)
    print(f"Kalibrace pro '{sensor_name}' byla uložena.")

def calculate_do(voltage_mv, temperature_c, cal_voltage, cal_temp):
    """Výpočet hodnoty DO na základě napětí a teploty."""
    try:
        temp_index = int(temperature_c)
        if temp_index < 0 or temp_index >= len(DO_TABLE):
            raise ValueError("Teplota mimo rozsah DO tabulky.")

        v_saturation = cal_voltage + 35 * temperature_c - cal_temp * 35
        do_value = voltage_mv * DO_TABLE[temp_index] / v_saturation
        return round(do_value, 2)
    except ValueError as e:
        print(f"Chyba při výpočtu DO: {e}")
        return None

def calibrate_do():
    """Kalibrační procedura DO senzoru."""
    print("=== Kalibrace DO senzoru ===")
    temperature_c = float(input("Zadejte aktuální teplotu (°C): "))
    voltage_mv = float(input("Zadejte aktuální napětí z ADC (mV): "))
    calibration_data["DO"]["voltage"] = voltage_mv
    calibration_data["DO"]["temperature"] = temperature_c
    save_calibration("DO", calibration_data["DO"])
    print("Kalibrace dokončena.")

def measure_do():
    """Měření hodnoty DO."""
    calibration = load_calibration("DO")
    if not calibration:
        print("Kalibrace není dostupná. Nejprve proveďte kalibraci.")
        return

    voltage_mv = float(input("Zadejte aktuální napětí z ADC (mV): "))
    temperature_c = DEFAULT_TEMP  # Lze přidat měření teploty
    do_value = calculate_do(
        voltage_mv,
        temperature_c,
        calibration["voltage"],
        calibration["temperature"]
    )
    print(f"Rozpuštěný kyslík: {do_value} µg/L ({do_value / 1000:.2f} mg/L)")

if __name__ == "__main__":
    while True:
        print("\n1: Kalibrace DO senzoru")
        print("2: Měření hodnoty DO")
        print("3: Ukončit program")
        choice = input("Vyberte možnost: ")

        if choice == "1":
            calibrate_do()
        elif choice == "2":
            measure_do()
        elif choice == "3":
            print("Program ukončen.")
            break
        else:
            print("Neplatná volba, zkuste to znovu.")
