import os
import sys
import pathlib
import shutil
import pandas as pd
import gzip
import re
import numpy as np
from collections import Counter

'''
Script for processing DEEPSOIL profile bundle files (.dpz) to individual
DEEPSOIL profiles (.dp)

This is particularly helpful for saving randomized profiles and assigning PWP
Generation Model parameters to each with respect to the base or reference 
profile.

The script assumes that both the 'Generate Excess Porewater Pressure' option and 
'Enable Dissipation' sub-option are enabled.
'''


class PWPGenModel(object):
    DISSIPATION = [
        'RU', #0.95,
        'CV', #0.1,
        'CV_EXPONENT' #0,
    ]

class SandVuceticDobry(PWPGenModel):
    REQUIRES_PARAMETERS = {
        'INPUT 1': 'PWP_F1', #1, 
        'INPUT 2': 'PWP_P', #1, 
        'INPUT 3': 'PWP_F2', #0.73,
        'INPUT 4': 'PWP_S', #1, 
        'INPUT 5': 'PWP_G', #0.02,
        'INPUT 6': 'PWP_V' #3.8
    }

class SandGreenMitchellPolito(PWPGenModel):
    REQUIRES_PARAMETERS = {
        'INPUT 1': 'PWP_ALPHA',#:[2]
        'INPUT 2': 'PWP_DR',#:[95]
        'INPUT 3': 'PWP_FC',#:[15]
        'INPUT 4': 'PWP_V'#:[3.8]
    }

class SandParkAhn(PWPGenModel):
    REQUIRES_PARAMETERS = {
        'INPUT 1': 'PWP_ALPHA',#:'0.7' 
        'INPUT 2': 'PWP_BETA',#:'0.7' 
        'INPUT 3': 'PWP_DRU1',#:'15' 
        'INPUT 4': 'PWP_CSRT',#:'0.3' 
        'INPUT 5': 'PWP_V'#:'3.8'
    }

class SandBerrillDavis(PWPGenModel):
    pass

class ClayMatasovic(PWPGenModel):
    REQUIRES_PARAMETERS = {
        'INPUT 1': 'PWP_S',#:'0.122'
        'INPUT 2': 'PWP_R',#:'0.522'
        'INPUT 3': 'PWP_A',#:'13.66'
        'INPUT 4': 'PWP_B',#:'-28.01'
        'INPUT 5': 'PWP_C',#:'16.508'
        'INPUT 6': 'PWP_D',#:'-2.149'
        'INPUT 7': 'PWP_G'#:'0.1'
    }

PWP_MODEL = {   "S_VD": SandVuceticDobry(), # Sand - Vucetic-Dobry model
                "S_GMP": SandGreenMitchellPolito(), # Sand - GMP model
                "G_PA": SandParkAhn(), # Sand - Park-Ahn model
                "S_BD": SandBerrillDavis(), # Sand - Berrill-Davis model
                "C_M": ClayMatasovic()  # Clay - Matasovic model
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

def gz_extract(directory):
    extension = ".gz"
    os.chdir(directory)
    for item in os.listdir(directory): # loop through items in dir
      if item.endswith(extension): # check for ".gz" extension
          gz_name = os.path.abspath(item) # get full path of files
          # get file name for file within
          file_name = (os.path.basename(gz_name)).rsplit('.',1)[0] 
          with gzip.open(gz_name,"rb") as f_in, open(file_name,"wb") as f_out:
              shutil.copyfileobj(f_in, f_out)
          os.remove(gz_name) # delete zipped file

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
    # Reads manually extracted folder (FOR NOW) because of zip/gzip issues
    parent_dir = os.path.dirname(os.path.abspath(zip_file))
    extracted_dir = os.path.join(os.path.join(parent_dir, 
                        os.path.splitext(zip_file)[0]))
    dir_list = os.listdir(extracted_dir)

    # Get list and number of randomized profiles
    rand_profiles = [i for i in dir_list if 'Profile' in i and '.' not in i]
    rand_profiles = [i for i in rand_profiles if not '_' in i]
    num_rands = len(rand_profiles) - 1

    # Read Mean Soil Profile definition
    with open(os.path.join(extracted_dir, 'Profile1'), 'r') as base_profile:
        # get file contents line by line and output a list
        contents = base_profile.readlines()
    
    idx = [(x,i) for x,i in enumerate(contents) if '[LAYER]' in i]
    num_idx = len(idx)
    
    # Create dict of layer info in Profile1 & 
    # then check if consistent with csv (TBA)
    Profile1 = {}
    b_layer_id = list()
    # Loop for each layer data in `contents` list
    for i,ln in list(reversed(list(enumerate(idx))))[1:]: 
        # Get layer info in Mean Profile
        l_data = contents[idx[i][0]:idx[i+1][0]]

        # Data cleanup
        l_data_clean = [s.strip('\t\n') for s in l_data]
        l_data_clean = [re.sub(r"[\([{})\]]", "", s) for s in l_data_clean]
        
        # Get thickness of layer from basic layer info
        [basic_l] = [re.findall(r'[^\s]+', l) for l in l_data_clean 
                                if 'THICKNESS' in l]
        basic_d = {s.split(':')[0]: float(s.split(':')[1]) for s in basic_l}
        
        # Insert line of PWP parameters in list to be written later in file
        l_PWP = [l.strip('LAYER:') for l in l_data_clean if 'LAYER:' in l]
        l_PWP = int(l_PWP[0])
        b_layer_id.append(l_PWP)
        PWP_model_data = layer_info[l_PWP]
        # Convert keys to uppercase
        PWP_model_data = {k.upper(): v for k,v in PWP_model_data.items()}

        # Map parameter objects
        model_id = PWP_model_data['MODEL ID']
        dsp = dict.fromkeys(PWP_MODEL[model_id].DISSIPATION)
        reqs = PWP_MODEL[model_id].REQUIRES_PARAMETERS
        PWP_reqs = {**dsp, **reqs}

        # Assemble matching data values
        PWP_inputs = {'PWP_MODEL': model_id}
        PWP_inputs.update( {PWP_reqs[k]:PWP_model_data[k] \
                        for k in PWP_model_data if k in PWP_reqs} )
        
        # Line to insert in Profile1 file in DEEPSOIL syntax
        line_PWP = ' '.join([f"[{k}]:[{v}]" for k,v in PWP_inputs.items()])
        l_data.insert(-1, '\t' + line_PWP + '\n')
        contents[idx[i][0]:idx[i+1][0]] = l_data

        # Save Profile1 data to dict
        Profile1[l_PWP] = {'BASIC': basic_d, 'PWP_MODEL': PWP_inputs}

    # Re-write Profile1 to a new .dp file
    with open(os.path.join(extracted_dir, 'Profile1.dp'), 'w') as base_profile:
        # Set config for ANALYSIS_TYPE to include PWP generation in NL analysis
        # Set config for DISSIPATION conditions
        SET_PWP = ('[ANALYSIS_TYPE]:[NONLINEAR+PWP]\n[DISSIPATION]:[TRUE] '
                   '[TOP_BOUNDARY_PERMEABLE]:[TRUE] '
                   '[BOTTOM_BOUNDARY_PERMEABLE]:[FALSE]\n')
        
        idx = [(x,i) for x,i in enumerate(contents) if '[ANALYSIS_TYPE]' in i]
        aidx, atag = idx[0]
        contents[aidx] = SET_PWP
        base_profile.writelines(contents)      

    print(f'Export of Profile1.dp is successful.')

    # Link Profile1 and ProfileX via model info
    rand_profiles.remove('Profile1')
    # Loop for all ProfileX
    for rprof in rand_profiles:
        with open(os.path.join(extracted_dir, rprof), 'r') as rprof_file:
            rprof_contents = rprof_file.readlines()
    
        # Get lines of basic layer info, including thickness
        rl_thk_lines = [l for l in rprof_contents if 'THICKNESS' in l]
        
        basic_l_coll = [re.sub(r"[\([{})\]]", "", s) for s in rl_thk_lines]
        basic_l_coll = [s.split() for s in basic_l_coll]
        # Convert to dict
        basic_d_coll = [{s.split(':')[0]: float(s.split(':')[1]) for s in d} 
                                    for d in basic_l_coll]
        
        # Get lines of basic layer info, including thickness
        rl_smodel_lines = [l for l in rprof_contents if 'MODEL' in l]
        
        smodel_l_coll = [re.sub(r"[\([{})\]]", "", s) for s in rl_smodel_lines]
        smodel_l_coll = [s.split() for s in smodel_l_coll]
        # Convert to dict
        smodel_d_coll = [{s.split(':')[0]: s.split(':')[1] for s in d} 
                                    for d in smodel_l_coll]
        
        # Get list of line index & layer id tuple pairs
        ridx_all = [(x,i) for x,i in enumerate(rprof_contents) 
                        if '[LAYER]' in i]
        
        # Line index up to Layer Top_of_Rock
        line_idx = [int(str(l).split(':')[0]) for l,_ in ridx_all]
        # Layer bounds 
        l_bounds = [l.strip() for _,l in ridx_all]
        l_bounds = [re.sub(r"[\([{})\]]", "", s) for s in l_bounds]
        l_bounds = [l.strip('LAYER:') for l in l_bounds if 'LAYER:' in l]
        l_bounds[-1] = len(l_bounds) # convert last element TOP_OF_ROCK
        l_bounds = [int(l) for l in l_bounds]
        l_soil_bounds = l_bounds[:-1] # remove last rock layer
        
        # Create dict of ProfileX data
        ProfileX = {k: {'BASIC':v1, 'SOIL_MODEL': v2} for k,v1,v2 in 
                        zip(l_soil_bounds, basic_d_coll, smodel_d_coll)}

        r_layer_str_coll = [float(ProfileX[t]['SOIL_MODEL']['STRENGTH']) for t in 
                                            l_soil_bounds]
        
        # Retrieve corresponding layers 
        # by counting unique STRENGTH values of sublayers
        str_counter = Counter(np.around(r_layer_str_coll, decimals=6))
       
        # Get list of number of sublayers per layer definition in ProfileX
        num_layers_coll = [n for _,n in list(str_counter.items())]
        l_top_idx = np.cumsum(np.insert(num_layers_coll, 0, 1))
        ridx = [(x,i) for (x,i) in list(zip(line_idx, l_bounds))
                            if i in l_top_idx]
        
        b_layer_id_iter = iter(b_layer_id)
        bl_id = next(b_layer_id_iter)
        # Loop for each sublayer data in `rprof_contents` list
        for i,ln in list(reversed(list(enumerate(l_bounds))))[1:]: 
            # Get layer info in ProfileX
            l_data = rprof_contents[ridx_all[i][0]:ridx_all[i+1][0]]
            
            # Data cleanup
            l_data_clean = [s.strip('\t\n') for s in l_data]
            l_data_clean = [re.sub(r"[\([{})\]]", "", s) for s in l_data_clean]
            
            # Insert line of PWP parameters in list to be written later in file
            # Get PWP model of corresponding layer of ProfileX to Profile1
            if (l_top_idx[:-1][bl_id-1]) > (i+1):
                bl_id = next(b_layer_id_iter)

            PWP_model_data = layer_info[bl_id]
            # Convert keys to uppercase
            PWP_model_data = {k.upper(): v for k,v in PWP_model_data.items()}

            # Map parameter objects
            model_id = PWP_model_data['MODEL ID']
            dsp = dict.fromkeys(PWP_MODEL[model_id].DISSIPATION)
            reqs = PWP_MODEL[model_id].REQUIRES_PARAMETERS
            PWP_reqs = {**dsp, **reqs}

            # Assemble matching data values
            PWP_inputs = {'PWP_MODEL': model_id}
            PWP_inputs.update( {PWP_reqs[k]:PWP_model_data[k] \
                            for k in PWP_model_data if k in PWP_reqs} )
            
            # Line to insert in Profile1 file in DEEPSOIL syntax
            line_PWP = ' '.join([f"[{k}]:[{v}]" for k,v in PWP_inputs.items()])
            l_data.insert(-1, '\t' + line_PWP + '\n')
            rprof_contents[ridx_all[i][0]:ridx_all[i+1][0]] = l_data

            # Save Profile1 data to dict
            ProfileX[i+1] = {'BASIC': basic_d, 'PWP_MODEL': PWP_inputs}

        # Re-write ProfileX to a new .dp file
        with open(os.path.join(extracted_dir, rprof+'.dp'), 'w') as rprof_file:
            # Set config for ANALYSIS_TYPE to include PWP generation 
            # Set config for DISSIPATION conditions
            SET_PWP = ('[ANALYSIS_TYPE]:[NONLINEAR+PWP]\n[DISSIPATION]:[TRUE] '
                    '[TOP_BOUNDARY_PERMEABLE]:[TRUE] '
                    '[BOTTOM_BOUNDARY_PERMEABLE]:[FALSE]\n')
            
            idx = [(x,i) for x,i in enumerate(rprof_contents) 
                                              if '[ANALYSIS_TYPE]' in i]
            aidx, atag = idx[0]
            rprof_contents[aidx] = SET_PWP
            rprof_file.writelines(rprof_contents)   

        print(f'Export of {rprof}.dp is successful.')
    # Delete zip file if it exists

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
    
def export_dp_to_zip(output_dir=None):
    '''
    Write and export DEEPSOIL all .dp files packaged in zip file.
    
    By default, this will output the zip package within the same directory.
    '''
    raise NotImplementedError

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
        dpz_to_zip = replace_file_ext(file_name, to_='gz')
        # Default file name to be read for PWP parameter csv files (for now)
        fcsv = os.path.splitext(dpz_to_zip)[0] + '_model-inputs.csv'
        layers_pwp = read_pwp_csv(fcsv) # read csv file and get layer info dict
        generate_dp_from_zip(dpz_to_zip, layer_info=layers_pwp)
