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

ec_sensor.begin()


def measure_and_calibrate_ec(ads1115, ec, temperature=25):
    try:
        ads1115.setAddr_ADS1115(0x48)
        ads1115.setGain(ADS1115_REG_CONFIG_PGA_6_144V)
        adc0 = ads1115.readVoltage(0)
        if adc0 is None:
            raise ValueError("Nepodařilo se přečíst hodnotu z ADS1115.")
        print(f"A0: {adc0['r']} mV")  # Zobrazení hodnoty v mV
        ec.calibration(adc0['r'], temperature)
        # print(f"EC senzor byl úspěšně kalibrován na hodnotu {adc0['r']} mV při teplotě {temperature}°C.")
    except Exception as e:
        print(f"Chyba při měření nebo kalibraci: {e}")


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
    
    while True:
        print("\n1: Měření EC hodnoty")
        print("2: Kalibrace EC senzoru")
        print("3: Ukončit program")
        choice = input("Vyberte možnost: ")

        if choice == "1":
            read_ec()
        elif choice == "2":
            # ec_sensor.calibration(adc0['r'],ec_sensor, 23)
            measure_and_calibrate_ec(ads1115,ec_sensor, 23)
        elif choice == "3":
            print("Program ukončen.")
            break
        else:
            print("Neplatná volba, zkuste to znovu.")
