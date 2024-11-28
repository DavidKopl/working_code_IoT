import sys
sys.path.append('/home/davidkopl/Documents/working_code_IoT/Python')
import time
import mh_z19
import Adafruit_DHT

ADS1115_REG_CONFIG_PGA_6_144V        = 0x00 # 6.144V range = Gain 2/3
ADS1115_REG_CONFIG_PGA_4_096V        = 0x02 # 4.096V range = Gain 1
ADS1115_REG_CONFIG_PGA_2_048V        = 0x04 # 2.048V range = Gain 2 (default)
ADS1115_REG_CONFIG_PGA_1_024V        = 0x06 # 1.024V range = Gain 4
ADS1115_REG_CONFIG_PGA_0_512V        = 0x08 # 0.512V range = Gain 8
ADS1115_REG_CONFIG_PGA_0_256V        = 0x0A # 0.256V range = Gain 16

from DFRobot_ADS1115 import ADS1115
from DFRobot_EC      import DFRobot_EC
from DFRobot_PH      import DFRobot_PH


ads1115 = ADS1115()
ec      = DFRobot_EC()
ph      = DFRobot_PH()
DHT_SENSOR = Adafruit_DHT.DHT22



# Konstanty
VREF = 5000    # Referenční napětí v mV
ADC_RES = 32768  # Rozlišení ADS1115 (16-bit)
TWO_POINT_CALIBRATION = 0
READ_TEMP = 25  # Teplota vody v °C
DHT_PIN = 4

# Kalibrační hodnoty
CAL1_V = 195  # mv
CAL1_T = 25   # ℃
CAL2_V = 1300 # mv
CAL2_T = 15   # ℃

DO_Table = [
    14460, 14220, 13820, 13440, 13090, 12740, 12420, 12110, 11810, 11530,
    11260, 11010, 10770, 10530, 10300, 10080, 9860, 9660, 9460, 9270,
    9080, 8900, 8730, 8570, 8410, 8250, 8110, 7960, 7820, 7690,
    7560, 7430, 7300, 7180, 7070, 6950, 6840, 6730, 6630, 6530, 6410
]
def read_do(voltage_mv, temperature_c):
    temperature_index = int(temperature_c)  # Nebo použij round(temperature_c) pro zaokrouhlení
    if temperature_index < 0 or temperature_index >= len(DO_Table):
        raise ValueError("Temperature index out of range for DO_Table")
    
    if TWO_POINT_CALIBRATION == 0:
        v_saturation = CAL1_V + 35 * temperature_c - CAL1_T * 35
        return (voltage_mv * DO_Table[temperature_index] // v_saturation)
    else:
        v_saturation = ((temperature_c - CAL2_T) * (CAL1_V - CAL2_V) // (CAL1_T - CAL2_T)) + CAL2_V
        return (voltage_mv * DO_Table[temperature_index] // v_saturation)

# def read_do(voltage_mv, temperature_c):
#     if TWO_POINT_CALIBRATION == 0:
#         v_saturation = CAL1_V + 35 * temperature_c - CAL1_T * 35
#         return (voltage_mv * DO_Table[temperature_c] // v_saturation)
#     else:
#         v_saturation = ((temperature_c - CAL2_T) * (CAL1_V - CAL2_V) // (CAL1_T - CAL2_T)) + CAL2_V
#         return (voltage_mv * DO_Table[temperature_c] // v_saturation)

ec.begin()
ph.begin()

while True:
    # Přečtěte teplotu (předpokládáme 25°C)
    
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    co2_value = mh_z19.read_from_pwm()
    
    # Nastavte zesílení a napětí
    ads1115.setGain(ADS1115_REG_CONFIG_PGA_6_144V)
    
    # Čtěte hodnoty z kanálů
    adc0 = ads1115.readVoltage(0)['r']  # Předpokládaný přístup k hodnotě
    adc1 = ads1115.readVoltage(1)['r']
    adc3 = ads1115.readVoltage(3)['r']
    
    # Konverze napětí na DO s teplotní kompenzací
    voltage_mv = VREF * adc3 // ADC_RES
    
    # Výpočet DO
    if temperature is not None:
        do_value = read_do(voltage_mv, temperature)
    else: 
        do_value = read_do(voltage_mv, 25.0)
    
    PH_working = True
    EC_working = True
    THRESHOLD = 10
    if adc0 <= THRESHOLD:
        print("EC senzor nepripojen")
        EC_working = False
    else:
        EC = ec.readEC(adc0, temperature)
        EC_working = True

    if adc1 <= THRESHOLD:
        print("PH senzor nepripojen")
        PH_working = False
    else:
        PH = ph.readPH(adc1, temperature)
        PH_working = True
     
    # Výstupní informace
    if adc0 is True and adc1 is True:
        print(f"Temperature: {temperature:.1f} C EC: {EC:.2f} ms/cm PH: {PH:.2f}")
    print(f"ADC readings: adc3={adc3} adc1={adc1} adc0={adc0}")
    print("Voltage (mv): ", adc3 * 5000 / 32768)
    print(f"CO2 Value: {co2_value} ppm")    
    if humidity is not None and temperature is not None:
        print(f"Teplota: {temperature:.1f} C   Vlhkost: {humidity:.1f} %")
    else:
        print("Chyba pri cteni ze senzoru DHT22.")
    print(f"DO: {do_value} mg/L")
    
    time.sleep(2)