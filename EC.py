import time
import sys
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# Globální proměnné
_kvalue = 1.0
_kvalueLow = 1.92
_kvalueHigh = 1.0

# Inicializace MCP3008 a kanálu
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.CE0)
mcp = MCP.MCP3008(spi, cs)
chan = AnalogIn(mcp, MCP.P0)  # Nastavení kanálu, zde P0

def initialize():
    """Načte kalibrační hodnoty z ecdata.txt nebo nastaví výchozí hodnoty."""
    global _kvalueLow, _kvalueHigh
    try:
        with open('ecdata.txt', 'r') as f:
            _kvalueLow = float(f.readline().strip('kvalueLow='))
            _kvalueHigh = float(f.readline().strip('kvalueHigh='))
    except:
        print("ecdata.txt ERROR! Please run reset function to create default settings.")
        sys.exit(1)

def read_ec(voltage, temperature=25.0):
    """Spočítá hodnotu EC na základě zadaného napětí a teploty."""
    global _kvalue, _kvalueLow, _kvalueHigh
    rawEC = 1000 * voltage / 820.0 / 200.0
    _kvalue = _kvalueHigh if rawEC * _kvalue > 2.5 else _kvalueLow
    return rawEC * _kvalue / (1.0 + 0.0185 * (temperature - 25.0))

def calibrate(voltage, temperature=25.0):
    """Kalibruje EC senzor podle zadaného napětí a teploty."""
    global _kvalueLow, _kvalueHigh
    rawEC = 1000 * voltage / 820.0 / 200.0
    if 0.9 < rawEC < 1.9:
        _kvalueLow = 820.0 * 200.0 * 1.413 * (1.0 + 0.0185 * (temperature - 25.0)) / 1000.0 / voltage
        save_calibration()
        print(">>>EC:1.413us/cm Calibration completed")
    elif 9 < rawEC < 16.8:
        _kvalueHigh = 820.0 * 200.0 * 12.88 * (1.0 + 0.0185 * (temperature - 25.0)) / 1000.0 / voltage
        save_calibration()
        print(">>>EC:12.88ms/cm Calibration completed")
    else:
        print(">>>Buffer Solution Error Try Again<<<")

def save_calibration():
    """Uloží kalibrační hodnoty do ecdata.txt."""
    with open('ecdata.txt', 'w') as f:
        f.write(f'kvalueLow={_kvalueLow}\n')
        f.write(f'kvalueHigh={_kvalueHigh}\n')

def reset():
    """Resetuje kalibrační hodnoty na výchozí hodnoty a uloží je do ecdata.txt."""
    global _kvalueLow, _kvalueHigh
    _kvalueLow, _kvalueHigh = 1.0, 1.0
    save_calibration()
    print(">>>Reset to default parameters<<<")

# Hlavní cyklus
initialize()

while True:
    # Čtení napětí a výpočet hodnoty EC
    voltage = chan.voltage
    temperature = 25  # Změňte podle potřeby nebo přidejte senzor pro měření teploty
    
    EC_value = read_ec(voltage, temperature)
    
    # Výstup hodnot
    print(f'Raw ADC Value: {chan.value}')
    print(f'ADC Voltage: {voltage:.2f} V')
    print(f'Elektrická konduktivita (EC): {EC_value:.4f} uS/cm')
    
    time.sleep(2)
