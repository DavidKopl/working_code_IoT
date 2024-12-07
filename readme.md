# MH_Z19B sensor
potreba propojit pres PWM pin 
- VCC 
- GND 
- PWM s GPIO12.

s pinem na PWM 5 od spoda strana 5V.
Knihovna mh_z19

> Je potreba senzor prumerovat klouzavym prumerem, kdyz je uzivatel u zarizeni, tak hodnoty bez problemu do 30 sekund vyleti z 600 na 1500 :/ coz je negativni efekt, klouzavy prumer, alespon na 20 min provozu by byl ok.
Ve skleniku je optimalni hodnota 1000-1500PPM. Relay by tedy melo dodavat CO2 do skleniku.
---
# DHT22 sensor
Data pin s 14, knihovna Adafruit_DHT

---
# PT1000 
Je potreba resistor, a v promenne resistor napsat jeji hodnotu.

Zapojeni na fotografii
> +by bylo dobre napsat funkci na klouzavi prumer. 
---


Instalace balicku
 1) activovat venv prostredi activate
    source ~/Documents/working_code_IoT/venv/bin/activate
    cd /home/davidkopl/Documents/working_code_IoT/Python/example


 2) pip install nazevbalicku

TODO: Umoznit ze serveru posilat prikaz na kalibraci EC, DO, PH

Pro debug automatickeho systemu
journalctl -u monitoring.service