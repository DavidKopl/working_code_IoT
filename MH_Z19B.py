import time
import mh_z19

while True:
    try:
        # Čtení hodnoty z PWM
        co2_value = mh_z19.read_from_pwm()
        
        # Zde můžete přidat jiné možnosti čtení
        # co2_value = mh_z19.read_from_pwm(range=2000)
        # co2_value = mh_z19.read_from_pwm(gpio=12, range=2000)
        
        # Výpis hodnoty CO2
        print(f"CO2 Value: {co2_value} ppm")
        
        # Pauza mezi měřeními, aby nedošlo k příliš častému čtení
        time.sleep(2)
        
    except Exception as e:
        print(f"Chyba pri cteni senzoru: {e}")
        break  # Pokud nastane chyba, cyklus se ukončí
