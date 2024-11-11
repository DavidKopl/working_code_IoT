import spidev
import time

# Inicializace SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Bus 0, Device 0
spi.max_speed_hz = 1350000

def read_adc(channel):
    # Čtení hodnoty z ADC
    if channel < 0 or channel > 7:
        raise ValueError("Channel must be between 0 and 7")
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    return ((adc[1] & 3) << 8) + adc[2]

def convert_to_ph(value):
    # Konverze ADC hodnoty na pH (přizpůsob podle potřeby)
    voltage = (value * 5.0) / 1023  # Napětí (0-5V)
    ph = 7 + ((2.5 - voltage) / 0.18)  # Uprav podle kalibrace
    return ph

try:
    while True:
        adc_value = read_adc(0)  # Čteme z kanálu 0
        ph_value = convert_to_ph(adc_value)
        print(f"pH Value: {ph_value:.2f}", f"adc: {adc_value:.2f}")
        time.sleep(1)  # Pauza 1 sekundu

except KeyboardInterrupt:
    spi.close()
