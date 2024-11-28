def read_do(voltage_mv, temperature_c):
#     if TWO_POINT_CALIBRATION == 0:
#         v_saturation = CAL1_V + 35 * temperature_c - CAL1_T * 35
#         return (voltage_mv * DO_Table[temperature_c] // v_saturation)
#     else:
#         v_saturation = ((temperature_c - CAL2_T) * (CAL1_V - CAL2_V) // (CAL1_T - CAL2_T)) + CAL2_V
#         return (voltage_mv * DO_Table[temperature_c] // v_saturation)
