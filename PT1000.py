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

# Vytvoření kanálu pro PT1000 (předpokládáme, že je připojen k P7)
chan = AnalogIn(mcp, MCP.P7)

# Hodnota referenčního odporu (1000 Ohm, jak uvádíš)
resistance = 1000  # Používáme referenční odpor 1000 Ohm

while True:
    # Získání hodnoty z ADC
    raw_adc_value = chan.value
    voltage = chan.voltage  # ADC napětí získáme přímo z objektu chan
    
    # Výpočet odporu pomocí děliče napětí
    thermResistance = (voltage * resistance) / (3.3 - voltage)  # Používáme 3.3V, ne 5V

    # Přepočet odporu na teplotu (pro PT1000)
    temperature = (thermResistance - 1000) / 3.85  # PT1000 linearita

    # Ladicí výstupy pro hodnoty
    print(f'Raw ADC Value: {raw_adc_value}')
    print(f'ADC Voltage: {voltage:.2f} V')
    print(f'ThermResistance: {thermResistance:.2f} Ohm')
    print(f'Temperature: {temperature:.2f} C')

    time.sleep(2)
