import Adafruit_DHT
import time

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

while True:
    vlhkost, teplota = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)


    time.sleep(2)