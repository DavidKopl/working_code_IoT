import busio
import digitalio
import board
import time
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# Vytvoření SPI sběrnice
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# Vytvoření CS (chip select)
cs = digitalio.DigitalInOut(board.CE0)

# Vytvoření MCP objektu
mcp = MCP.MCP3008(spi, cs)

# Vytvoření kanálu pro pH senzor
chan = AnalogIn(mcp, MCP.P3)  # Používáme kanál 3

while True:
    raw_adc_value = chan.value
    adc_voltage = chan.voltage

    print(f'Raw ADC Value: {raw_adc_value}')
    print(f'ADC Voltage: {adc_voltage:.2f} V')
    time.sleep(2)