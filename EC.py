import busio
import digitalio
import board
import time
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
from GreenPonik_EC import GreenPonik_EC

# Create the SPI bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# Create the CS (chip select)
cs = digitalio.DigitalInOut(board.CE0)

# Create the MCP object
mcp = MCP.MCP3008(spi, cs)

# Create the channel (assuming it is connected to P7)
chan = AnalogIn(mcp, MCP.P0)

# Calibration constant (replace with your sensor's actual calibration factor)
# This is an example value, adjust it based on your sensor's datasheet or calibration.


while True:
    # Read raw ADC value and calculate voltage
    raw_adc_value = chan.value
    voltage = chan.voltage  # Voltage corresponding to the ADC value
    temperature = 25
    # EC = ec.readEC(voltage, temperature)


# Výstup výsledku
    # print(f'Elektricka kondukce (EC): {EC} uS/cm')


    # Print the values
    print(f'Raw ADC Value: {raw_adc_value}')
    print(f'ADC Voltage: {voltage:.2f} V')
    
    time.sleep(2)
