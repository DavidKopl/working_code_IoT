import time
import sys
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
from DFRobot_EC import DFRobot_EC

# Inicializace třídy pro měření EC
ec = DFRobot_EC()

# Inicializace MCP3008 a kanálu
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.CE0)
mcp = MCP.MCP3008(spi, cs)
chan = AnalogIn(mcp, MCP.P0)  # Nastavení kanálu, zde P0

# Inicializace EC zařízení
ec.begin()

# Hlavní smyčka
while True:
    # Čtení napětí z kanálu
    voltage = chan.voltage
    temperature = 25  # Změňte podle potřeby nebo přidejte senzor pro měření teploty
    
    # Zobrazení napětí
    print(f"Voltage: {voltage:.2f} V")
    
    # Kalibrace podle napětí, pokud je v příslušném rozsahu
    ec.calibration(voltage, temperature)
    
    # Výpočet hodnoty EC
    EC = ec.readEC(voltage, temperature)
    print(f"EC: {EC:.6f} mS/cm")

    # Čekání 2 sekundy před dalším měřením
    time.sleep(2)
