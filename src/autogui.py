import sys
import subprocess
import pyautogui
import time
import os
import psutil


def dp_autogui(dp_file_path):
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
        pyautogui.press('space') # select all motions

        # Select `Next` from *Input Motion Selection*
        time.sleep(2.75)
        if result.poll() is not None:
        # Return code 3221225477 or hex 0xC0000005 STATUS_ACCESS_VIOLATION
            print(f'Program crashed. returncode: {result.returncode}')
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
        while is_process_running('soil64.exe'): 
            time.sleep(1.0)
        
        pyautogui.hotkey('alt', 'f', 'e') # exit DEEPSOIL

    print(f'Program executed successfully. returncode: {result.returncode}')
    return result.returncode

def dp_autogui_dir():
    pass

def is_process_running(process_name):
    '''
    Check if there is a running process that contains the given `process_name`.
    '''
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if process_name.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, 
                psutil.ZombieProcess):
            pass
    return False;


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        dp_file = input('Path to .dp file: ')
    else:
        dp_file = sys.argv[1]
    
    if os.path.isfile(dp_file) and dp_file.lower().endswith('.dp'):
        dp_autogui(dp_file)
    else:
        raise FileNotFoundError("Invalid file.")