import os
import sys
import pathlib
import shutil
import pandas as pd
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
                "C_M"  # Clay - Matasovic model
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
    
def generate_dp_from_zip(zip_file, layer_info=None, output_dir=None):
    '''
    Read zip file, open and parse ProfileX files, and then insert PWP parameters

    :param zip_file:
        Name of zip file
    :type zip_file: ``str``
    :param layer_info:
        Dictionary of layer info with PWP inputs
    :type layer_info: ``dict``
    :param \**kwargs:
        See below

    :Keyword Arguments:
    * `output_dir` (``str``) --
        Name of output file
    '''      
    # Open zip file with context manager
    with ZipFile(zip_file, 'r') as zip:
        # Read without extracting the ProfileX files
        data = zip.read('Profile1') # override base profile

        # Count profiles and then loop for all
        # Link Profile 1 and ProfileX via thickness info
        print(data)   

        # Parse Profile to insert PWP model parameters
        #   Loop until detect [MRDF] tag
        #   Format writer -> "[]" syntax
        #   Just insert PWP model parameters to each layer in ProfileX
        #   Export to ProfileX.dp files

def read_pwp_csv(fname=None):
    '''
    Read and parse csv file containing PWP parameters.

    This requires a csv file with file name:
        '{fcsv}_model-inputs.csv'
    
    Returns a dictionary of layer information and PWP model inputs
    '''
    if fname is None:
        fcsv = '{fcsv}_model-inputs.csv'
    else:
        fcsv = fname[:-4] + 'model-inputs.csv' # remove file ext and add latter

    layers_pwp = {}
    
    return layers_pwp
    
def export_dp(output_dir=None):
    '''
    Write and export DEEPSOIL all .dp files packaged in zip file.
    
    By default, this will output the zip package within the same directory.
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
        # Get file name from argv command line; NOT YET TESTED
        file_name = sys.argv[1]

    # Get file extension of argv
    file_ext = pathlib.Path(file_name).suffix
    if not file_ext.lower() == ".dpz":
        raise ValueError('File extension is invalid.')
    else:
        dpz_to_zip = rename_dpz(file_name)
    
    read_pwp_csv(file_name)
    generate_dp_from_zip(dpz_to_zip)
