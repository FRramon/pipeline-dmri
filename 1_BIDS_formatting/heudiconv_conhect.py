import os
import shutil
import subprocess
import csv
import pandas as pd
import re
import sys
import json


from anonymize_conhect import *
from heudiconv_parameters import *

# Check if the correct number of command-line arguments is provided
if len(sys.argv) != 2:
    print("Usage: python heudiconv_conhect.py <base_dir> ")
    sys.exit(1)

base_dir = sys.argv[1]
print(base_dir)

def atoi(text):
    return int(text) if text.isdigit() else text
def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]
   
source_data_dir = os.path.join(base_dir,"data")

anonymize_conhect(source_data_dir)

correct_names(source_data_dir)
###########################################
# Before this step
# Make sure that folder convertall and rawdata exists
# 1 : Run :

#docker run --rm -it \
#-v /home/francoisramon/bids_tutorial:/base:ro \
#-v /home/francoisramon/bids_tutorial/convertall:/output \
#nipy/heudiconv:latest \
#-d /base/rawdata/sub-{subject}/ses-{session}/01-RawData/*/* \
#-f convertall \
#-s 01 \
#-ss 001 \
#-c none \
#-o /output

# This will create a .heudiconv hidden file (access with ls -a)
# The .tsv file will able to create a heuristic.py file

# This file is used to encod raw data into bids formatting through this pipeline

#############################################

################################################
# Step 1 : Params and set working directories    #
################################################

###Running parameters ##################


base = base_dir
base_output = os.path.join(base_dir,"nifti3")
codes_path = os.path.join(base_dir,"code","1_BIDS_formatting")

heuristic_file = os.path.join(codes_path, heuristic_filename)
heuristic = heuristic_file  # convertall or heuristic_file

#groups = os.listdir(source_data_dir)
#groups = ['Patients']
####################################################
#                   Step 2                         #
####################################################

#use heudiconv with heuristic.py file to encode raw data with the heuristic.py subject after subject and session after session   

for g in groups:

    os.chdir(os.path.join(source_data_dir,g)) 
    subjects_raw = os.listdir()
    pattern = re.compile(r'^sub-\d{2}')
    subjects = [s for s in subjects_raw if pattern.match(s)]
    for i,nsub in enumerate(subjects):

        sessions_raw = os.listdir(source_data_dir + "/" + g +"/" + subjects[i])
        pattern_ses = re.compile(r'^ses-\d{3}')
        sessions = [s for s in sessions_raw if pattern_ses.match(s)]

        for itSes in range(len(sessions)):

            subject_id = subjects[i][4:]
            session_id = sessions[itSes][4:]
            subject_folder = 'sub-' + subject_id
            session_folder = 'ses-' + session_id

            print(f'Running in group {g} on subject ID {subject_folder}, session ID {session_folder}\n')

            output = os.path.join(base_output,g)
            if DOheudiconv:
                print(f'    START: heudiconv')
                dicom_dir_pattern = "/base/data/Patients/sub-{subject}/ses-{session}/01-RawData/*/*"
               # dicom_dir_pattern = os.path.join(base,'test', 'sub-{subject}', 'ses-{session}','01-RawData','*', '*')
                bashCommand = f"docker run --rm -it -v {base}:/base -v {output}:/output nipy/heudiconv:latest -d {dicom_dir_pattern} -f base/code/1_BIDS_formatting/heuristic_conhect.py -s {subject_id} -ss {session_id} -c dcm2niix -o /output -b --overwrite"
                print(bashCommand)
                if not dryrun_heudiconv:
                    process = subprocess.run(bashCommand,shell = True)

            print(f'    DONE: heudiconv ')
            print(f'    START: Checking PE direction')
            ses_path = os.path.join(base_output,g,subject_folder,session_folder)
            
            hasDWI = os.path.isdir(os.path.join(ses_path,'dwi'))
            print(hasDWI)
            if hasDWI and DOrename:
               
                dwi_path = os.path.join(ses_path,'dwi')
                files = os.listdir(dwi_path)
                json_files = [f for f in files if os.path.splitext(f)[1] =='.json']

                for f in json_files:
                    print(f'    Looking at: {f}')
                    with open(os.path.join(dwi_path,f)) as user_file:
                        js = json.load(user_file)
                        direction = js['PhaseEncodingPolarityGE']
                        print(f'        PhaseEncodingPolarityGE: {direction}')
                        # Flipped -> PA; Unflipped -> AP
                        initial_dir = os.path.splitext(f)[0].split('_')[3].split('-')[1]
                        dir_nb = os.path.splitext(f)[0].split('_')[2].split('-')[1]
                        print(f'        Number of directions: {dir_nb}')
                        print(f'        Initial direction: {initial_dir}')
                        if direction == 'Flipped':
                            corrected_dir = 'PA'
                        elif direction == 'Unflipped':
                            corrected_dir = 'AP'

                        nifti_files = [f for f in files if os.path.splitext(f)[1] =='.gz']
                        nifti_file = [f for f in nifti_files if f.split('_')[2].split('-')[1] == dir_nb][0]

                        bvec_files = [f for f in files if os.path.splitext(f)[1] =='.bvec']
                        bvec_file = [f for f in bvec_files if f.split('_')[2].split('-')[1] == dir_nb][0]

                        bval_files = [f for f in files if os.path.splitext(f)[1] =='.bval']
                        bval_file = [f for f in bval_files if f.split('_')[2].split('-')[1] == dir_nb][0]

                        print(f'        Associated files:')
                        print(f'            {nifti_file}')
                        print(f'            {bval_file}')
                        print(f'            {bvec_file}')

                        if initial_dir == corrected_dir:
                            print(f'        Decision: No correction')                      
                        else:
                            file_attribute = nifti_file.split('_')[:5]
                            print(file_attribute)
                            separator = '_'
                            corrected_common_name = separator.join(file_attribute[:3]) + '_dir-' + corrected_dir + '_dwi'

                            corrected_json = corrected_common_name + '.json'
                            corrected_nifti = corrected_common_name + '.nii.gz'
                            corrected_bval = corrected_common_name + '.bval'
                            corrected_bvec = corrected_common_name + '.bvec'
    
                            print('         Corrected names: ')
                            print(os.path.join(dwi_path,corrected_nifti))
                            print(os.path.join(dwi_path,corrected_bval))
                            print(os.path.join(dwi_path,corrected_bvec))

                            if not dryrun_rename:

                                os.rename(os.path.join(dwi_path,f),os.path.join(dwi_path,corrected_json))
                                os.rename(os.path.join(dwi_path,nifti_file),os.path.join(dwi_path,corrected_nifti))
                                os.rename(os.path.join(dwi_path,bval_file),os.path.join(dwi_path,corrected_bval))
                                os.rename(os.path.join(dwi_path,bvec_file),os.path.join(dwi_path,corrected_bvec))

                    print(f'    Finish correction of: {f}')
            else:
                print("No DWI")
print("Finish")
