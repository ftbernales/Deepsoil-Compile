import os
from re import T
import numpy as np

input_path = input('Enter full path of suite to be scaled: ')
output_path = input('Enter output directory: ')

# input_path = "C:\Users\francis.bernales\Desktop\input"
# output_path = "C:\Users\francis.bernales\Desktop\DEEPSOIL Format"

for root, dirs, files in os.walk(input_path):
    for file in files:
        with open(os.path.join(input_path, os.path.splitext(file)[0] + \
            ".txt"), 'r') as f:
            f.readline() # skip first line
            # first_line = f.readline()
            # NPTS = int(first_line.split()[0])
            # DT = float(first_line.split()[1])

            lines = f.readlines()
            t = []
            ACC = []
            for line in lines:
                t.append(float(line.split()[0]))
                ACC.append(float(line.split()[1]))

            DT = np.diff(t)[0]
            if not np.all(np.fabs(np.diff(t) - DT) < 1E-10):
                raise ValueError(f"Time step in {os.path.abspath(t)} \
                                    is not consistent!")   

            NPTS = len(t)

            # Scale accelerogram
            SF = 1.0
            ACC = SF*np.array(ACC)

            nl = '\n'
            tab = '\t'
            lines = [f'{a:.3f}{tab}{b:.5e}{nl}' for a,b in zip(t,ACC)]
            # str(a) + "\t" + str(b) + '\n'
            
        with open(os.path.join(output_path, os.path.splitext(file)[0] + \
            ".txt"), 'w') as f:
            # f.write("Time (s)   Acc (g)\n")
            f.write(str(NPTS) + "  " + str(DT) + "\n")
            f.writelines(lines)
            