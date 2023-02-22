import os
import numpy as np
import pyrotd

def calc_suite_rs(folder_acc=None, damping=0.05):
    from matching_assessment import _import_time_series
    from intensity_measures import get_response_spectrum_pair
    from sm_utils import convert_accel_units

    if folder_acc is None:
        raise ValueError("Path to accelerogram directory not specified!")

    # set a period list with same length as DEEPSOIL
    osc_periods = np.logspace(-1, 2, 113) 
    H1_acc, H2_acc, time_step = _import_time_series(folder_acc)

    sax, say = get_response_spectrum_pair(H1_acc, time_step, H2_acc,
        time_step, osc_periods, damping=damping, units="cm/s/s",
        method="Frequency Domain")

    sax = convert_accel_units(sax, from_='cm/s/s', to_='g')
    say = convert_accel_units(say, from_='cm/s/s', to_='g')
    print(sax)
    print(say)
    
if __name__ == '__main__':
    import sys
    sys.path.append('C:\\Users\\francis.bernales\\Documents\\Projects\\Deepsoil-Compile\\src')
    calc_suite_rs(folder_acc='C:/Users/francis.bernales/Desktop/Matching_Assessment/data/input_files')