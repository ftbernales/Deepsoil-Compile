import sys
import subprocess
import pyautogui
import time
import os
import psutil

'''
This script contains functions for running the DEEPSOIL program using 
`pyautogui`.

If this module is ran directly, she will ask for a directory path containing the
.dp files to analyze/execute.
'''

def dp_autogui(dp_file_path):
    '''
    This function uses the `dp_file_path` to run a single .dp file automatically
    in the DEEPSOIL GUI.

    :param dp_file_path:
        File name of DEEPSOIL .dp profile
    :type dp_file_path: ``str``
    
    Returns the returncode via the subprocess module.

    Checks whether DEEPSOIL program is installed to be added in the future.
    '''
    with subprocess.Popen([r"C:\Program Files"
                            r"\University of Illinois at Urbana-Champaign"
                            r"\DEEPSOIL 7.0\DEEPSOIL.exe", 
                            # execute if DEEPSOIL program executable exists
    ], stdin=subprocess.PIPE, stdout=subprocess.PIPE) as result:
        time.sleep(0.5)

        # Open .dp file
        pyautogui.press('alt')
        pyautogui.press('f')
        pyautogui.press('o')
        pyautogui.write(dp_file_path)
        pyautogui.press('enter')

        # Select `Next` from *Analysis Type Definition*
        pyautogui.press('tab', presses=32)
        pyautogui.press('space')

        # Select `Check Data` from *Soil Profile Definition*
        pyautogui.press('tab', presses=18)
        pyautogui.press('space')

        # Select `Next` from *Soil Profile Definition*
        pyautogui.press('space')

        # Input Motion Selection
        pyautogui.press('tab', presses=17)
        pyautogui.press('space') # de-select generation of motion plots
        pyautogui.press('tab', presses=3)
        pyautogui.press('space') # select ALL motions in Input Motion Directory

        # Select `Next` from *Input Motion Selection*
        time.sleep(2.75)
        if result.poll() is not None:
        # Return code 3221225477 or hex 0xC0000005 STATUS_ACCESS_VIOLATION
            print(f'DEEPSOIL crashed! (returncode: {result.returncode})')
            return result.returncode
        pyautogui.press('tab', presses=10)
        pyautogui.press('space')

        # Select `Next` from *Viscous/Small-Strain Damping Definition*
        # time.sleep(0.1)
        pyautogui.press('tab', presses=18)
        pyautogui.press('space')
        
        # Analysis Control Definition
        # time.sleep(0.1)
        pyautogui.press('tab', presses=26)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.write('0.005') # default maximum strain increment %
        pyautogui.press('tab')
        pyautogui.press('down', presses=2)
        pyautogui.press('space') # de-select Displacement Animation
        pyautogui.press('tab', presses=18)
        pyautogui.press('space') # Analyze
        
        # do until child process of DEEPSOIL is running
        time.sleep(1.0)
        while is_process_running('soil64'): 
            time.sleep(1.0)
        
        pyautogui.hotkey('alt', 'f', 'e') # exit DEEPSOIL

    print(f'Program executed successfully for {dp_file_path} (returncode: {result.returncode})')
    return result.returncode

def dp_autogui_dir(dp_dirname):
    '''
    This function uses the `dp_dirname` to run multiple .dp files in a directory
    automatically in the DEEPSOIL GUI.

    Internally calls *dp_autogui* function for each .dp in `dp_dirname`

    If DEEPSOIL crashes for a given .dp run, it will automatically attempt to
    re-run the same .dp file.

    :param dp_dirname:
        Path to directory containing .dp profiles to run
    :type dp_dirname: ``str``
    '''
    if not os.path.isdir(dp_dirname):
        raise FileNotFoundError("Invalid directory.")

    dp_coll = [f for f in os.listdir(dp_dirname) if f.lower().endswith('.dp')]
    if len(dp_coll) == 0: # empty list
        raise FileNotFoundError("No .dp files found.")
    
    for dp in dp_coll:
        run_dp = None
        while run_dp != 0:
            run_dp = dp_autogui( os.path.join( dp_dirname, dp ) )


def is_process_running(process_name):
    '''
    Check if there is a running process that contains the given `process_name`.
    '''
    # Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if process_name.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False;


if __name__ == "__main__":
    # If script is ran directly, execute dp_autogui for entire directory
    if len(sys.argv) <= 1:
        dp_dir = input('Path of directory containing .dp files to run: ')
    else:
        dp_dir = sys.argv[1]

    dp_autogui_dir(dp_dir)