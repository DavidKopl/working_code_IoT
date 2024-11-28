import sys
import time
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
TWO_POINT_CALIBRATION = 0
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4
THRESHOLD = 10
SERVER_URL = "http://192.168.0.69:3000/data"

# Kalibrace DO
CAL1_V = 195
CAL1_T = 25
CAL2_V = 1300
CAL2_T = 15
DO_Table = [
    14460, 14220, 13820, 13440, 13090, 12740, 12420, 12110, 11810, 11530,
    11260, 11010, 10770, 10530, 10300, 10080, 9860, 9660, 9460, 9270,
    9080, 8900, 8730, 8570, 8410, 8250, 8110, 7960, 7820, 7690,
    7560, 7430, 7300, 7180, 7070, 6950, 6840, 6730, 6630, 6530, 6410
]

# Inicializace
ads1115 = ADS1115()
ec = DFRobot_EC()
ph = DFRobot_PH()
ec.begin()
ph.begin()

def read_do(voltage_mv, temperature_c):
    temperature_index = int(temperature_c)
    if temperature_index < 0 or temperature_index >= len(DO_Table):
        raise ValueError("Temperature index out of range for DO_Table")
    
    if TWO_POINT_CALIBRATION == 0:
        v_saturation = CAL1_V + 35 * temperature_c - CAL1_T * 35
        return (voltage_mv * DO_Table[temperature_index] // v_saturation)
    else:
        v_saturation = ((temperature_c - CAL2_T) * (CAL1_V - CAL2_V) // (CAL1_T - CAL2_T)) + CAL2_V
        return (voltage_mv * DO_Table[temperature_index] // v_saturation)

while True:
    # Čtení teploty a vlhkosti
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    co2_value = mh_z19.read_from_pwm()

    # Čtení hodnot z ADC
    ads1115.setGain(ADS1115_REG_CONFIG_PGA_6_144V)
    adc0 = ads1115.readVoltage(0)['r']
    adc1 = ads1115.readVoltage(1)['r']
    adc2 = ads1115.readVoltage(2)['r']
    voltage_mv = VREF * adc2 // ADC_RES

    # Zjištění funkčnosti EC a PH senzorů
    EC, PH , do_value = None, None, None
    if adc0 > THRESHOLD:
        EC = ec.readEC(adc0, temperature if temperature else 25)
    else:
        print("EC senzor nepripojen")

    if adc1 > 2800 or adc1 < 600:
        print("PH senzor nepripojen")
    else:
        PH = ph.readPH(adc1, temperature)

    if adc2 > THRESHOLD:
        do_value = read_do(voltage_mv, temperature if temperature else 25)
    else:
        print("DO senzor nepripojen")


    try:
        co2_value = mh_z19.read_from_pwm()
    except Exception as e:
        print(f"CO2 read failed: {e}")
        co2_value = {"co2": None}
    # Sestavení dat pro odeslání
    data = {
        "sensor_id": "device_1",
        "temperature": temperature,
        "humidity": humidity,
        "co2": co2_value.get("co2") if co2_value else None, 
        "ec": EC,
        "ph": PH,
        "do": do_value,
        "adc_readings": {"adc0": adc0, "adc1": adc1, "adc2": adc2}
    }

    # Odeslání dat na server
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(SERVER_URL, data=json.dumps(data), headers=headers)
        print(f"Server responded with status: {response.status_code}")
        print(response.text)
    except Exception as e:
        print(f"Failed to send data: {e}")

    # Zpoždění mezi iteracemi
    time.sleep(3)
