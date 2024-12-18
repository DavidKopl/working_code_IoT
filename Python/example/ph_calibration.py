import sys
import time
import json
sys.path.append('/home/davidkopl/Documents/working_code_IoT/Python')

from DFRobot_ADS1115 import ADS1115
from DFRobot_PH      import DFRobot_PH

# Nastavení zisku pro ADS1115
ADS1115_REG_CONFIG_PGA_6_144V = 0x00  # 6.144V range = Gain 2/3

# Inicializace senzorů
ads1115 = ADS1115()
ph = DFRobot_PH()

ph.begin()

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

# Použití senzoru
def measure_ph(temperature=25):
    """ Měření pH pomocí senzoru s použitím kalibrační hodnoty. """
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
            calibrate_ph_sensor(ads1115,ph, 23)
        elif action == "m":
            measure_ph()
        elif action == "q":
            print("Ukončuji program.")
            break
        else:
            print("Neznámá volba, zkuste to znovu.")