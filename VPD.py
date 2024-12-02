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

def calculate_rh_for_vpd(temp_c, target_vpd, leaf_temp_c):
    # Výpočet SVP
    svp = 0.6108 * math.exp((17.27 * temp_c) / (temp_c + 237.3))

    svp_leaf = calculate_svp(leaf_temp_c)
    # Výpočet RH na základě požadovaného VPD
    rh = 100 * (1 - target_vpd / svp_leaf)
    return round(rh, 2)

# Testovací hodnoty
temperature = 15.0
  # °C
humidity = 71 # %
target_vpd = 1.2  # kPa

# Výpočet požadované vlhkosti
rh_for_vpd_optimum = calculate_rh_for_vpd(temperature, target_vpd,temperature-2)
rh_for_vpd_min = calculate_rh_for_vpd(temperature, target_vpd+0.2,temperature-2)
rh_for_vpd_max = calculate_rh_for_vpd(temperature, target_vpd-0.2,temperature-2)
current_vpd = calculate_vpd(temperature, humidity)
leaf_vpd = calculate_leaf_vpd(temperature, temperature-2, humidity)
print("Clone: 0.6-1.0 kPa, Vegetace: 1.0-1.2 kPa, Rostlina: 1.2-1.5 kPa")
print(f"Pro dosažení leaf_VPD {target_vpd} kPa při teplotě {temperature}°C je potřebná vlhkost min: {rh_for_vpd_min}% - max: {rh_for_vpd_max}%.\nA optimum je: {rh_for_vpd_optimum}%")
print(f"Air VPD: {current_vpd} kPa")
print(f"Leaft VPD: {leaf_vpd} kPa")
 