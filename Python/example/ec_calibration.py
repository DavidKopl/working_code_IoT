import sys
import time
from datetime import datetime

# Přidání cesty pro vlastní knihovny
sys.path.append('/home/davidkopl/Documents/working_code_IoT/Python')

# Importy
from DFRobot_ADS1115 import ADS1115
from DFRobot_EC import DFRobot_EC

# Nastavení zisku pro ADS1115
ADS1115_REG_CONFIG_PGA_6_144V = 0x00  # 6.144V range = Gain 2/3

# Inicializace ADS1115 a EC senzoru
ads1115 = ADS1115()
ec_sensor = DFRobot_EC()

def initialize_sensors():
    """Inicializace EC senzoru."""
    ec_sensor.begin()
    print("EC sensor initialized.")

def calibrate_ec():
    """
    Funkce pro kalibraci EC senzoru.
    Uživateli umožní zadat hodnotu standardního roztoku
    a na jejím základě provede kalibraci.
    """
    try:
        print("=== EC Calibration ===")
        input("Připravte prosím standardní roztok a stiskněte Enter...")
        
        # Nastavení ADS1115
        ads1115.setAddr_ADS1115(0x48)
        ads1115.setGain(ADS1115_REG_CONFIG_PGA_6_144V)
        
        # Změření napětí z ADC na kanálu 0
        adc_value = ads1115.readVoltage(0)
        if 'r' not in adc_value:
            print("Error: Invalid ADC reading during calibration.")
            return
        
        # Zobrazení změřeného napětí
        voltage = adc_value['r']
        print(f"Naměřené napětí: {voltage:.3f} V")
        
        # Zadání hodnoty standardního roztoku od uživatele
        standard_ec = float(input("Zadejte hodnotu EC standardního roztoku (v ms/cm): "))
        
        # Kalibrace senzoru
        ec_sensor.calibration(voltage, standard_ec)
        print("Kalibrace dokončena.")

    except Exception as e:
        print(f"Error during calibration: {e}")

def read_temperature():
    """Funkce pro čtení teploty - statická hodnota 25 °C."""
    return 25.0

def read_ec():
    """Funkce pro čtení EC hodnoty s kompenzací teploty."""
    try:
        # Nastavení ADS1115
        ads1115.setAddr_ADS1115(0x48)
        ads1115.setGain(ADS1115_REG_CONFIG_PGA_6_144V)
        
        # Čtení napětí z ADC
        adc_value = ads1115.readVoltage(0)
        if 'r' not in adc_value:
            print("Error: Invalid ADC value.")
            return
        
        # Čtení teploty
        temperature = read_temperature()
        
        # Výpočet EC hodnoty
        ec_value = ec_sensor.readEC(adc_value['r'], temperature)
        
        # Výstup
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Temperature: {temperature:.1f} °C, EC: {ec_value:.2f} ms/cm a EC: {ec_value * 1000:.0f} uS/cm")
    
    except Exception as e:
        print(f"Error while reading EC: {e}")

if __name__ == "__main__":
    initialize_sensors()
    
    while True:
        print("\n1: Měření EC hodnoty")
        print("2: Kalibrace EC senzoru")
        print("3: Ukončit program")
        choice = input("Vyberte možnost: ")

        if choice == "1":
            read_ec()
        elif choice == "2":
            calibrate_ec()
        elif choice == "3":
            print("Program ukončen.")
            break
        else:
            print("Neplatná volba, zkuste to znovu.")
