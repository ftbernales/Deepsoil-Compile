import os
import sys
import math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from intensity_measures import get_husid, get_response_spectrum
from sm_utils import convert_accel_units as conv
from utils.plotting_matched import read_from_xlsx
from matplotlib.ticker import FuncFormatter

"""
Set of scripts for generating RS plots from Excel file
"""
CONFIG = dict()
CONFIG['matching_periods'] = (0.25, 2.5)

plt.rcParams["grid.linestyle"] = "-"
plt.rcParams["grid.linewidth"] = 0.75
plt.rcParams["axes.formatter.useoffset"] = False


def plot_rs_from_xlsx(periods=None):
    data = read_from_xlsx(CONFIG)
    data_targ = read_targ_from_xlsx(CONFIG)
    for ws in data:
        time_steps1 = np.diff(data[ws]['ORIG/SCALED']['Orig_Time'])
        assert np.allclose(time_steps1, time_steps1[0]) is True
        time_step1 = time_steps1[0]
        time_steps2 = np.diff(data[ws]['MATCHED']['Match_Time'])
        assert np.allclose(time_steps2, time_steps2[0]) is True
        time_step2 = time_steps2[0]
        
        if periods is None:
            periods = np.logspace(-2, 1, num=113)

        spectrum_original = get_response_spectrum(
            data[ws]['ORIG/SCALED']['Orig_Acc'], time_step1, periods, 
            damping=0.05, units="g")[0]
        
        spectrum_matched = get_response_spectrum(
            data[ws]['MATCHED']['Match_Acc'], time_step2, periods, 
            damping=0.05, units="g")[0]
        
        # convert to g units of acceleration
        spectrum1_g = conv(spectrum_original["Pseudo-Acceleration"], 
                          from_='cm/s/s', to_='g')
        
        # convert to g units of acceleration
        spectrum2_g = conv(spectrum_matched["Pseudo-Acceleration"], 
                          from_='cm/s/s', to_='g')
        
        plot_rs_comparison(data_targ['Targ_Periods'], data_targ['Targ_PSA'], 
                           periods, spectrum1_g, spectrum2_g, 
                           ws + ' RS.png'
                           )

def get_sheets(filename, print_list=True):
    """
    Get a printed list of worksheets in an Excel file
    """
    wb = pd.ExcelFile(filename, engine='openpyxl')
    
    wsnames = wb.sheet_names # get list of worksheet names
    if print_list:
        for name in wsnames:
            print(f"'{name}'", end=" ")

def read_targ_from_xlsx(config):
    """
    Retrieve data from Excel file based on provided config parameters
    """
    filename = config['fname']
    wb = pd.ExcelFile(filename, engine='openpyxl')
    
    wsnames = wb.sheet_names # get list of worksheet names
    req_sheets = config['targ']
    # convert to upper case for case-insensitive comparison later
    req_sheets_upper = [s.upper() for s in req_sheets]

    selected_sheets = [ws for ws in wsnames if ws.upper() in req_sheets_upper]

    if len(selected_sheets) > 0:
        raise ValueError("Select only the sheet with target spectra!")
    
    if req_sheets not in wsnames:
        raise ValueError("Sheet name is invalid!")

    cols = ['Targ_Periods', 'Targ_PSA']
    
    df_targ = wb.parse(sheet_name=req_sheets, usecols="A:B", names=cols, 
                       skiprows=1)
    df_targ.dropna(inplace=True)    

    wb.close()

    return df_targ

def plot_rs_comparison(targ_periods, targ_psa, matched_periods, psa1, psa2, 
                       fname='rs.png', output_format='png'):
    """
    Plot the comparison of original & matched PSA with respect to target spectra
    """
    psa_logmin = math.floor(
        math.log10(min(targ_psa.min(), psa1.min(), psa2.min())))
    psa_logmax = math.ceil(
        math.log10(max(targ_psa.max(), psa1.max(), psa2.max())))
    
    fig = plt.figure()
    fig.patch.set_linewidth(1.)  
    fig.patch.set_edgecolor('black')  
    ax1 = fig.add_subplot(1, 2, 1)
    ax1.loglog(targ_periods, targ_psa, color='red', label='TARGET')
    ax1.loglog(matched_periods, psa1, color='black', label='SCALED')
    ax1.set_xlim(xmin=min(targ_periods.min(), matched_periods.min()), 
                 xmax=max(targ_periods.max(), matched_periods.max()) + 0.1)
    ax1.set_ylim(ymin=10**psa_logmin, 
                 ymax=10**psa_logmax)
    ax1.plot(CONFIG['matching_periods'][0]*np.ones(2), ax1.get_ybound(), 
             color='green')
    ax1.plot(CONFIG['matching_periods'][1]*np.ones(2), ax1.get_ybound(), 
             color='green')
    ax1.grid(which='major', color='#D9D9D9')
    ax1.grid(which='minor', color='#F2F2F2')
    ax1.legend(loc='best')
    for axis in [ax1.xaxis, ax1.yaxis]:
        formatter = FuncFormatter(lambda y, _: '{:.16g}'.format(y))
        axis.set_major_formatter(formatter)
    ax1.fill_between(np.array(CONFIG['matching_periods']), 
                     ax1.get_ybound()[0], ax1.get_ybound()[1], 
                     color='#00B050', alpha=0.3)

    ax2 = fig.add_subplot(1, 2, 2)
    ax2.loglog(targ_periods, targ_psa, color='red', label='TARGET')
    ax2.loglog(matched_periods, psa2, color='black', label='MATCHED')
    ax2.set_xlim(xmin=min(targ_periods.min(), matched_periods.min()), 
                 xmax=max(targ_periods.max(), matched_periods.max()) + 0.1)
    ax2.set_ylim(ymin=10**psa_logmin, 
                 ymax=10**psa_logmax)
    ax2.plot(CONFIG['matching_periods'][0]*np.ones(2), ax2.get_ybound(), 
             color='green')
    ax2.plot(CONFIG['matching_periods'][1]*np.ones(2), ax2.get_ybound(), 
             color='green')
    ax2.grid(which='major', color='#D9D9D9')
    ax2.grid(which='minor', color='#F2F2F2')
    ax2.legend(loc='best')
    for axis in [ax2.xaxis, ax2.yaxis]:
        formatter = FuncFormatter(lambda y, _: '{:.16g}'.format(y))
        axis.set_major_formatter(formatter)
    ax2.fill_between(np.array(CONFIG['matching_periods']), 
                     ax2.get_ybound()[0], ax2.get_ybound()[1], 
                     color='#00B050', alpha=0.3)
    
    fig.supxlabel('Period $T$ (s)')
    fig.supylabel('Spectral Acceleration $S_a$ (g)')
    fig.tight_layout()
    fig.savefig(fname, format=output_format)
    plt.close()


if __name__ == '__main__':
    CONFIG['fname'] = sys.argv[1]
    if not os.path.isfile(CONFIG['fname']):
        raise FileNotFoundError
    
    CONFIG['targ'] = sys.argv[2]
    CONFIG['sheets'] = sys.argv[3:]
    plot_rs_from_xlsx()