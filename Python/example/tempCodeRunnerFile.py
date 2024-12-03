
config = fetch_config(SERVER_URL)

DHT_PIN = config.get("dht_pin", 4) if config else 4
config_update_time = config.get("config_update_time", 600) if config else 600
relay_pins = config.get("relay_pins", [10, 17, 27, 22]) if config else [10, 17, 27, 22]
adc_threshold = config.get("adc_threshold", 10) if config else 10
last_temperature = config.get("last_temperature", 25) if config else 25
last_humidity = config.get("last_humidity", 50) if config else 50
temp_hum_err = config.get("temp_hum_err", False) if config else False
EC_err = config.get("ec_err", False) if config else False
Ph_err = config.get("ph_err", False) if config else False
DO_err = config.get("do_err", False) if config else False
ONE_POINT_CALIBRATION = config.get("one_point_calibration", True) if config else True
CAL1_V = config.get("cal1_v", 195) if config else 195
CAL1_T = config.get("cal1_t", 25) if config else 25

DO_Table = config.get(
    "do_table",
    [
        14460, 14220, 13820, 13440, 13090, 12740, 12420, 12110, 11810, 11530,
        11260, 11010, 10770, 10530, 10300, 10080, 9860, 9660, 9460, 9270,
        9080, 8900, 8730, 8570, 8410, 8250, 8110, 7960, 7820, 7690,
        7560, 7430, 7300, 7180, 7070, 6950, 6840, 6730, 6630, 6530, 6410,
    ],
) if config else [
    14460, 14220, 13820, 13440, 13090, 12740, 12420, 12110, 11810, 11530,
    11260, 11010, 10770, 10530, 10300, 10080, 9860, 9660, 9460, 9270,
    9080, 8900, 8730, 8570, 8410, 8250, 8110, 7960, 7820, 7690,
    7560, 7430, 7300, 7180, 7070, 6950, 6840, 6730, 6630, 6530, 6410,
]

maxHumidity = config.get("max_humidity", 90) if config else 90
maxHumidityGap = config.get("max_humidity_gap", 10) if config else 10
maxTemperature = config.get("max_temperature", 30) if config else 30
maxTemperatureGap = config.get("max_temperature_gap", 10) if config else 10
minTemperature = config.get("min_temperature", 15) if config else 15
minTemperatureGap = config.get("min_temperature_gap", 10) if config else 10
minCO = config.get("min_co", 600) if config else 600
minCOGap = config.get("min_co_gap", 200) if config else 200

target_vpd = config.get("target_vpd", 1.2) if config else 1.2
co2_min = config.get("co2_min", 600) if config else 600
co2_max = config.get("co2_max", 800) if config else 800
temp_min = config.get("temp_min", 15) if config else 15
temp_max = config.get("temp_max", 30) if config else 30
humidity_min = config.get("humidity_min", 50) if config else 50
humidity_max = config.get("humidity_max", 90) if config else 90