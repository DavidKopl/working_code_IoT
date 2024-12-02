import math


def calculate_svp(temp_c):
    # Výpočet SVP (nasycený tlak vodní páry)
    return 0.6108 * math.exp((17.27 * temp_c) / (temp_c + 237.3))

def calculate_vpd(temp_c, rh):
    # Výpočet SVP
    svp = 0.6108 * math.exp((17.27 * temp_c) / (temp_c + 237.3))
    # Výpočet VPD
    vpd = svp * (1 - rh / 100)
    return round(vpd,2)

def calculate_leaf_vpd(air_temp_c, leaf_temp_c, rh):
    # SVP pro vzduch a list
    svp_air = calculate_svp(air_temp_c)
    svp_leaf = calculate_svp(leaf_temp_c)
    # Výpočet Leaf VPD
    leaf_vpd = svp_leaf - (svp_air * (rh / 100))
    return round(leaf_vpd, 2)

def calculate_rh_for_vpd(temp_c, target_vpd):
    # Výpočet SVP
    svp = 0.6108 * math.exp((17.27 * temp_c) / (temp_c + 237.3))
    # Výpočet RH na základě požadovaného VPD
    rh = 100 * (1 - target_vpd / svp)
    return round(rh, 2)

# Testovací hodnoty
temperature = 25  # °C
humidity = 50 # %
target_vpd = 1.2  # kPa

# Výpočet požadované vlhkosti
rh_for_vpd = calculate_rh_for_vpd(temperature, target_vpd)
current_vpd = calculate_vpd(temperature, humidity)
leaf_vpd = calculate_leaf_vpd(temperature, temperature-2, humidity)
print(f"Pro dosažení VPD {target_vpd} kPa při teplotě {temperature}°C je potřebná vlhkost {rh_for_vpd}%.")
print(f"Air VPD: {current_vpd} kPa")
print(f"Leaft VPD: {leaf_vpd} kPa")
