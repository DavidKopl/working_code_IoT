import sys
sys.path.append('/home/davidkopl/Documents/working_code_IoT/Python')
import time
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

VREF = 5000  # Referenční napětí v mV
ADC_RES = 1024  # Rozlišení ADC
TWO_POINT_CALIBRATION = 0

CAL1_V = 1600  # Kalibrační napětí při teplotě CAL1_T (mV)
CAL1_T = 25    # Kalibrační teplota 1 (°C)
CAL2_V = 1300  # Kalibrační napětí při teplotě CAL2_T (mV)
CAL2_T = 15    # Kalibrační teplota 2 (°C)

DO_Table = [
    14460, 14220, 13820, 13440, 13090, 12740, 12420, 12110, 11810, 11530,
    11260, 11010, 10770, 10530, 10300, 10080, 9860, 9660, 9460, 9270,
    9080, 8900, 8730, 8570, 8410, 8250, 8110, 7960, 7820, 7690,
    7560, 7430, 7300, 7180, 7070, 6950, 6840, 6730, 6630, 6530, 6410
]

def readDO(voltage_mv, temperature_c):
    """Výpočet koncentrace rozpuštěného kyslíku (DO)."""
    if TWO_POINT_CALIBRATION == 0:
        V_saturation = CAL1_V + 35 * temperature_c - CAL1_T * 35
        return (voltage_mv * DO_Table[temperature_c] // V_saturation)
    else:
        V_saturation = ((temperature_c - CAL2_T) * (CAL1_V - CAL2_V) // (CAL1_T - CAL2_T)) + CAL2_V
        return (voltage_mv * DO_Table[temperature_c] // V_saturation)

ec.begin()
ph.begin()
while True:
    # Čtení teploty (předpokládáme konstantní hodnotu teploty)
    temperature = 25

    # Nastavení adresy ADS1115
    ads1115.setAddr_ADS1115(0x48)

    # Nastavení zisku pro ADS1115
    ads1115.setGain(ADS1115_REG_CONFIG_PGA_6_144V)

    # Čtení napětí z ADC kanálů
    adc0 = ads1115.readVoltage(0)  # Napětí z kanálu 0
    adc1 = ads1115.readVoltage(1)  # Napětí z kanálu 1
    adc2 = ads1115.readVoltage(2)  # Napětí z kanálu 2 pro DO

    # Výpočet napětí DO
    # adc_voltage_DO = VREF * adc2 / ADC_RES
    adc_voltage_DO = VREF * adc2['r'] / ADC_RES


    # Výpočet hodnoty DO
    DO = readDO(adc2, temperature)

    # Výpočet EC a pH
    EC = ec.readEC(adc0, temperature)
    PH = ph.readPH(adc1, temperature)

    # Výpis výsledků
    print(f"Teplota: {temperature} °C, EC: {EC:.2f} ms/cm, PH: {PH:.2f}, DO: {DO:.2f} mg/L")

    # Pauza mezi měřeními
    time.sleep(1.0)

  




