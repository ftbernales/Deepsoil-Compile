import subprocess
import pyautogui
import time

def dp_autogui(dp_file_path):
    result = subprocess.Popen([r"C:\Program Files"
                            r"\University of Illinois at Urbana-Champaign"
                            r"\DEEPSOIL 7.0\DEEPSOIL.exe",
    ])
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
    time.sleep(1.0)
    pyautogui.press('tab', presses=10)
    pyautogui.press('space')

    # Select `Next` from *Viscous/Small-Strain Damping Definition*
    time.sleep(0.75)
    pyautogui.press('tab', presses=18)
    pyautogui.press('space')

    # Analysis Control Definition
    time.sleep(0.75)
    pyautogui.press('tab', presses=26)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.write('0.005') # default maximum strain increment %
    pyautogui.press('tab')
    pyautogui.press('down', presses=2)
    pyautogui.press('space') # de-select Displacement Animation
    pyautogui.press('tab', presses=18)
    pyautogui.press('space') # Analyze

if __name__ == "__main__":
    dp_file = (r'C:\Users\AMH-L91\OneDrive - AMH Philippines, Inc\
        NP22.080 THEIDI Samal-Davao Connector SHA\06 NP22.080 WORK FILES\06 SRA\
            03C DEEPSOIL (1,000-Year)\03 BH-NB-06\02 PWP\NB-06_PWP\Profile1.dp')
    dp_autogui(dp_file)