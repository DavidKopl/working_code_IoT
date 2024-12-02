import math

def calculate_vpd(temp_c, rh):
    # Výpočet SVP
    svp = 0.6108 * math.exp((17.27 * temp_c) / (temp_c + 237.3))
    # Výpočet VPD
    vpd = svp * (1 - rh / 100)
    return round(vpd,2)

def calculate_rh_for_vpd(temp_c, target_vpd):
    # Výpočet SVP
    svp = 0.6108 * math.exp((17.27 * temp_c) / (temp_c + 237.3))
    # Výpočet RH na základě požadovaného VPD
    rh = 100 * (1 - target_vpd / svp)
    return round(rh, 2)

# Testovací hodnoty
temperature = 30  # °C
humidity = 55 # %
target_vpd = 1.2  # kPa

# Výpočet požadované vlhkosti
rh_for_vpd = calculate_rh_for_vpd(temperature, target_vpd)
current_vpd = calculate_vpd(temperature, humidity)
print(f"Pro dosažení VPD {target_vpd} kPa při teplotě {temperature}°C je potřebná vlhkost {rh_for_vpd}%.")
print(f"Current VPD: {current_vpd} kPa")
