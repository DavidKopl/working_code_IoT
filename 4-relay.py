import RPi.GPIO as GPIO
import time

# Nastavení GPIO pinů pro relé
relay_pins = [17, 27, 22, 10]  # GPIO čísla (přizpůsobte podle zapojení)

def setup():
    GPIO.setmode(GPIO.BCM)  # Použití číslování GPIO pinů
    GPIO.setwarnings(False)  # Vypnutí varování
    # Nastavení pinů jako výstupy
    for pin in relay_pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)  # Relé vypnuto (závisí na typu relé)

def relay_on(pin):
    GPIO.output(pin, GPIO.LOW)  # Zapnutí relé (LOW u aktivního LOW relé)

def relay_off(pin):
    GPIO.output(pin, GPIO.HIGH)  # Vypnutí relé (HIGH u aktivního LOW relé)

def cleanup():
    GPIO.cleanup()  # Reset GPIO pinů do výchozího stavu

if __name__ == "__main__":
    try:
        setup()
        while True:
            # Postupné spínání relé
            for pin in relay_pins:
                print(f"Zapínám relé na GPIO {pin}")
                relay_on(pin)
                time.sleep(5)  # Relé zapnuto na 1 sekundu
                print(f"Vypínám relé na GPIO {pin}")
                relay_off(pin)
                time.sleep(1)  # Relé vypnuto na 1 sekundu
    except KeyboardInterrupt:
        print("Ukončuji program...")
    finally:
        cleanup()
