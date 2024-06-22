import os
import sys
import warnings
import math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


"""
Set of scripts for generating AVD plots from Excel file
"""
CONFIG = dict()

plt.rcParams["font.family"] = "Calibri"
plt.rcParams["figure.figsize"] = (11.64, 5.27)
plt.rcParams["lines.linewidth"] = 0.75
plt.rcParams["axes.autolimit_mode"] = "round_numbers"
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False
plt.rcParams["axes.grid"] = True
plt.rcParams["axes.grid.axis"] = "y"
plt.rcParams["grid.linestyle"] = "--"
plt.rcParams["grid.color"] = "#7F7F7F"
plt.rcParams["xtick.bottom"] = False
plt.rcParams["ytick.left"] = False


def plot_avd_from_xlsx():
    data = read_from_xlsx(CONFIG)
    for ws in data:
        plot_acc_comparison(data[ws]['ORIG/SCALED']['Orig_Time'],
                            data[ws]['ORIG/SCALED']['Orig_Acc'],
                            data[ws]['MATCHED']['Match_Time'],
                            data[ws]['MATCHED']['Match_Acc'],
                            ws + ' Acc.svg')
        plot_vel_comparison(data[ws]['ORIG/SCALED']['Orig_Time'],
                            data[ws]['ORIG/SCALED']['Orig_Vel'],
                            data[ws]['MATCHED']['Match_Time'],
                            data[ws]['MATCHED']['Match_Vel'],
                            ws + ' Vel.svg')
        plot_disp_comparison(data[ws]['ORIG/SCALED']['Orig_Time'],
                             data[ws]['ORIG/SCALED']['Orig_Disp'],
                             data[ws]['MATCHED']['Match_Time'],
                             data[ws]['MATCHED']['Match_Disp'],
                             ws + ' Disp.svg')
        plot_ai_comparison(data[ws]['ORIG/SCALED']['Orig_Time'],
                           data[ws]['ORIG/SCALED']['Orig_AI'],
                           data[ws]['MATCHED']['Match_Time'],
                           data[ws]['MATCHED']['Match_AI'],
                           ws + ' AI.svg')

def read_from_xlsx(config):
    """
    Retrieve data from Excel file based on provided config parameters
    """
    data_dict = dict()
    filename = config['fname']
    wb = pd.ExcelFile(filename, engine='openpyxl')
    
    wsnames = wb.sheet_names # get list of worksheet names
    req_sheets = config['sheets']
    # convert to upper case for case-insensitive comparison later
    req_sheets_upper = [s.upper() for s in req_sheets]

    selected_sheets = [ws for ws in wsnames if ws.upper() in req_sheets_upper]

    if not len(selected_sheets):
        raise ValueError("Sheet names are invalid!")

    invalid_sheets = set(req_sheets).difference(set(selected_sheets))
    if len(invalid_sheets) > 0:
        warnings.warn(f"Invalid sheets {invalid_sheets} will be skipped.")

    cols = ['Orig_Time', 'Orig_Acc', 'Orig_Vel', 'Orig_Disp', 'Orig_AI',
            'Match_Time', 'Match_Acc', 'Match_Vel', 'Match_Disp', 'Match_AI']
    
    for ws in selected_sheets:
        df = wb.parse(sheet_name=ws, usecols="A:E,V:Z", names=cols)

        df_orig = df.loc[:,cols[:5]]
        df_orig.dropna(inplace=True)
        df_match = df.loc[:,cols[5:]]
        df_match.dropna(inplace=True)

        data_dict[ws] = {"ORIG/SCALED": df_orig,
                         "MATCHED": df_match}
    
    wb.close()

    return data_dict

def plot_acc_comparison(t1, acc1, t2, acc2, fname='acc.svg', 
                        output_format='svg'):
    """
    Plot the comparison of original/scaled & matched acceleration time histories
    """
    fig = plt.figure()
    fig.patch.set_linewidth(1.)  
    fig.patch.set_edgecolor('black')  
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.plot(t1, acc1, color='red', label='SCALED')
    ax1.plot(t2, acc2, color='black', label='MATCHED')
    ax1.legend(loc='best')

    t_end = t1.max()
    t_lim = math.ceil(t_end / 10.0) * 10
    for i in range(6, 11):
        if (int(round(t_lim)) % i) == 0:
            tmajor = np.linspace(0., float(t_lim), num=i+1)
            break
    
    ax1.set_xlim(xmin=0, xmax=t_lim)
    ax1.set_xticks(tmajor)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Acceleration (g)')
    fig.tight_layout()
    fig.savefig(fname, format=output_format)
    plt.close()

def plot_vel_comparison(t1, vel1, t2, vel2, fname='vel.svg', 
                        output_format='svg'):
    """
    Plot the comparison of original/scaled & matched velocity time histories
    """
    fig = plt.figure()
    fig.patch.set_linewidth(1.)  
    fig.patch.set_edgecolor('black')  
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.plot(t1, vel1, color='red', label='SCALED')
    ax1.plot(t2, vel2, color='black', label='MATCHED')
    ax1.legend(loc='best')
    
    t_end = t1.max()
    t_lim = math.ceil(t_end / 10.0) * 10
    for i in range(6, 11):
        if (int(round(t_lim)) % i) == 0:
            tmajor = np.linspace(0., float(t_lim), num=i+1)
            break
    
    ax1.set_xlim(xmin=0, xmax=t_lim)
    ax1.set_xticks(tmajor)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Velocity (cm/s)')
    fig.tight_layout()
    fig.savefig(fname, format=output_format)
    plt.close()

def plot_disp_comparison(t1, disp1, t2, disp2, fname='disp.svg', 
                         output_format='svg'):
    """
    Plot the comparison of original/scaled & matched displacement time histories
    """
    fig = plt.figure()
    fig.patch.set_linewidth(1.)  
    fig.patch.set_edgecolor('black')  
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.plot(t1, disp1, color='red', label='SCALED')
    ax1.plot(t2, disp2, color='black', label='MATCHED')
    ax1.legend(loc='best')
    
    t_end = t1.max()
    t_lim = math.ceil(t_end / 10.0) * 10
    for i in range(6, 11):
        if (int(round(t_lim)) % i) == 0:
            tmajor = np.linspace(0., float(t_lim), num=i+1)
            break
    
    ax1.set_xlim(xmin=0, xmax=t_lim)
    ax1.set_xticks(tmajor)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Displacement (cm)')
    fig.tight_layout()
    fig.savefig(fname, format=output_format)
    plt.close()

def plot_ai_comparison(t1, ai1, t2, ai2, fname='ai.svg', output_format='svg'):
    """
    Plot the comparison of (normalized) Arias Intensity with respect to time
    """
    fig = plt.figure()
    fig.patch.set_linewidth(1.)  
    fig.patch.set_edgecolor('black')  
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.plot(t1, ai1, color='red', label='SCALED')
    ax1.plot(t2, ai2, color='black', label='MATCHED')
    ax1.legend(loc='best')
    
    t_end = t1.max()
    t_lim = math.ceil(t_end / 10.0) * 10
    for i in range(6, 11):
        if (int(round(t_lim)) % i) == 0:
            tmajor = np.linspace(0., float(t_lim), num=i+1)
            break
    
    ax1.set_xlim(xmin=0, xmax=t_lim)
    ax1.set_xticks(tmajor)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Normalized Arias Intensity (%)')
    fig.tight_layout()
    fig.savefig(fname, format=output_format)
    plt.close()


if __name__ == '__main__':
    CONFIG['fname'] = sys.argv[1]
    if not os.path.isfile(CONFIG['fname']):
        raise FileNotFoundError
    
    CONFIG['sheets'] = sys.argv[2:]
    plot_avd_from_xlsx()