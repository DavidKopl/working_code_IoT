import time
import sys
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
from DFRobot_EC import DFRobot_EC

ec = DFRobot_EC()
# Inicializace MCP3008 a kanálu
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.CE0)
mcp = MCP.MCP3008(spi, cs)
chan = AnalogIn(mcp, MCP.P0)  # Nastavení kanálu, zde P0

ec.begin()
while True:
    # Čtení napětí a výpočet hodnoty EC
    voltage = chan.voltage
    temperature = 25  # Změňte podle potřeby nebo přidejte senzor pro měření teploty
    print(voltage)
    # EC_value = read_ec(voltage, temperature)
	# EC = ec.readEC(voltage['r'],temperature)
    EC = ec.readEC(voltage, temperature)
    print(f"EC: {EC:.6f}")
    time.sleep(2)
