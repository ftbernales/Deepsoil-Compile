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

def replace_file_ext(fname, to_='zip'):
    '''
    Replace extension of file while retaining original copy
    '''
    temp = 'copy_' + fname
    shutil.copy(fname, temp)
    p = pathlib.Path(fname)
    new_p = p.replace(p.with_suffix('.' + to_))
    os.replace(temp, temp[len('copy_'):])
    return new_p
    
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
        # print(data)

        # Parse Profile to insert PWP model parameters
        #   Loop until detect [MRDF] tag
        #   Format writer -> "[]" syntax
        #   Just insert PWP model parameters to each layer in ProfileX
        #   Export to ProfileX.dp files
        #   Delete zip file

def read_pwp_csv(fname=None):
    '''
    Read and parse csv file containing PWP parameters.
    
    Returns a dictionary of layer information and PWP model inputs
    '''
    if fname is None: # do by default
        raise FileNotFoundError # raise exception if no fname entered

    # Read csv file, skip first 5 rows with docs, set Layer ID as index col
    df_layers_pwp = pd.read_csv(fname, skiprows=5, index_col=0)
    
    # Process columns
    col_names = list(df_layers_pwp.columns.values) # get list of col names
    new_col_names = [item.replace('\n', ' ') for item in col_names] # clear '\n'
    df_layers_pwp.columns = new_col_names # replace with new col names w/o '\n'
    df_layers_pwp.drop(df_layers_pwp.columns[
        df_layers_pwp.columns.str.contains('unnamed', case=False)],
        axis = 1, inplace = True) # remove unnamed columns
    
    # Drop NaN index values
    df_layers_pwp = df_layers_pwp.loc[df_layers_pwp.index.dropna()]
    # Convert layer index to int
    df_layers_pwp.index = df_layers_pwp.index.astype("int")
    # Convert df to dict
    layers_pwp = df_layers_pwp.to_dict('index')
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
        dpz_to_zip = replace_file_ext(file_name, to_='zip')
        # Default file name for PWP parameter csv files (for now)
        fcsv = os.path.splitext(dpz_to_zip)[0] + '_model-inputs.csv'
        layers_pwp = read_pwp_csv(fcsv) # read csv file and get layer info dict
        generate_dp_from_zip(dpz_to_zip) # generate dp files
