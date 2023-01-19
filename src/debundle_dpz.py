import os
import sys
import pathlib


'''
Script for processing DEEPSOIL profile bundle files (.dpz) to individual
DEEPSOIL profiles (.dp)

This is particularly helpful for saving randomized profiles and assigning PWP
Generation Model parameters to each with respect to the base or reference 
profile.

The script assumes that both the 'Generate Excess Porewater Pressure' option and 
'Enable Dissipation' sub-option are enabled.
'''

PWP_MODEL = {   "S_VD", # Sand - Vucetic-Dobry model
                "S_GMP",# Sand - Green-Mitchell-Polito model
                "S_PA", # Sand - Park-Ahn model
                "S_BD", # Sand - Berrill-Davis model
                "C_M",  # Clay - Matasovic model
                "A_G"   # Any - Generalized model
            }

REQUIRES_PARAMETERS = {

}

PWP_MODEL = {
    RU:0.95,
    CV:0.1,
    CV_EXPONENT:0,
    PWP_F1:1, 
    PWP_P:1, 
    PWP_F2:0.73,
    PWP_S:1, 
    PWP_G:0.02,
    PWP_V:3.8
}

# Rename .dpz to .zip
#   Except if .dpz not found
#   Open ProfileX via context manager

# Parse for PWP model parameters
#   Loop until 
#   Detect [MRDF] tag
#   Format writer -> "[]" syntax
#   Just insert PWP model parameters to each layer in ProfileX

# Export all .dp files


if __name__ == "__main__":
    if sys.argv[1]:
        # Get file name from argv command line
        file_name = sys.argv[1]
    else:
        # Find all dpz files in current directory
        dpz_list = [file for file in os.listdir() if file.endswith('.dpz')]
        if len(dpz_list) > 1:
            print(*dpz_list, sep="\n")
            file_name = input("Choose dpz file from list: ")
        else:
            file_name = dpz_list[0]

    file_ext = pathlib.Path(file_name).suffix
    if not file_ext.lower() == ".dpz":
