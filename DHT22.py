import Adafruit_DHT
import time

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 14

while True:
    vlhkost, teplota = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)

    if vlhkost is not None and teplota is not None:
        print(f"Teplota: {teplota:.1f} C   Vlhkost: {vlhkost:.1f}%")
    else:
        print("Chyba pri cteni ze senzoru DHT22.")
    time.sleep(2)