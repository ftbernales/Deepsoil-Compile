import os
import sys
import pathlib
import shutil
from zipfile import ZipFile

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
                "G_PA", # Sand - Park-Ahn model
                "S_BD", # Sand - Berrill-Davis model
                "C_M",  # Clay - Matasovic model
                "A_G"   # Any - Generalized model
            }


class PWPGenModel(object):
    PWP_MODEL = {
        'RU', #0.95,
        'CV', #0.1,
        'CV_EXPONENT', #0,
    }

class SandVuceticDobry(PWPGenModel):
    REQUIRES_PARAMETERS = {
        'PWP_F1', #1, 
        'PWP_P', #1, 
        'PWP_F2', #0.73,
        'PWP_S', #1, 
        'PWP_G', #0.02,
        'PWP_V' #3.8
    }

class SandGreenMitchellPolito(PWPGenModel):
    REQUIRES_PARAMETERS = {
        'PWP_ALPHA'#:[2],
        'PWP_DR'#:[95],
        'PWP_FC'#:[15],
        'PWP_V'#:[3.8]
    }

class SandParkAhn(PWPGenModel):
    REQUIRES_PARAMETERS = {
        'PWP_ALPHA',#:'0.7' 
        'PWP_BETA',#:'0.7' 
        'PWP_DRU1',#:'15' 
        'PWP_CSRT',#:'0.3' 
        'PWP_V',#:'3.8'
    }

class SandBerrillDavis(PWPGenModel):
    pass

class ClayMatasovic(PWPGenModel):
    REQUIRES_PARAMETERS = {
        'PWP_S'#:'0.122'
        'PWP_R'#:'0.522'
        'PWP_A'#:'13.66'
        'PWP_B'#:'-28.01'
        'PWP_C'#:'16.508'
        'PWP_D'#:'-2.149'
        'PWP_G'#:'0.1'
    }

class Generalized(PWPGenModel):
    pass

def rename_dpz(fname):
    '''
    Replace extension of .dpz file to .zip while retaining original copy
    '''
    temp = 'copy_' + fname
    shutil.copy(fname, temp)
    p = pathlib.Path(fname)
    if not os.path.isfile(p): # Check if file exists, else rename file extension
        p.rename(p.with_suffix('.zip'))
    os.replace(temp, temp[len('copy_'):])
    return p
    
def parse_pwp_params(fname):
    '''
    Read zip file, open ProfileX files, and parse for PWP parameters
    '''
    # Open zip file with context manager
    with ZipFile(fname, 'r') as zip:
        # Read without extracting the ProfileX files
        data = zip.read('Profile1')     
        print(data)   

        
    # Parse for PWP model parameters
    #   Loop until 
    #   Detect [MRDF] tag
    #   Format writer -> "[]" syntax
    #   Just insert PWP model parameters to each layer in ProfileX

    # export_dp()
    
def export_dp():
    '''
    Write and export DEEPSOIL all .dp files in same dir
    '''
    pass

if __name__ == "__main__":
    if len(sys.argv) > 0:
        # Find all dpz files in current directory
        dpz_list = [file for file in os.listdir() if file.endswith('.dpz')]
        if len(dpz_list) > 1:
            print(*dpz_list, sep="\n")
            file_name = input("Choose dpz file from list: ")
        elif len(dpz_list) == 1:
            # Get only file found
            file_name = dpz_list[0]
        else:
            # Raise exception if no dpz file found
            raise FileNotFoundError('No dpz file found.')
    else:
        # Get file name from argv command line
        file_name = sys.argv[1]

    # Get file extension of argv
    file_ext = pathlib.Path(file_name).suffix
    if not file_ext.lower() == ".dpz":
        raise ValueError('File extension is invalid.')

    dpz_to_zip = rename_dpz(file_name)
    parse_pwp_params(dpz_to_zip)
