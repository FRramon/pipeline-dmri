import os
import subprocess
from bids.layout import BIDSLayout

######                    Instructions                   #######

convert2bids = False
run_pipeline = False
createMatrixes = False
QAcheck = False
bundleSegmentation= True

source_dir = '/mnt/CONHECT_data'

#################################################################
#########         BIDS Formatting & Correct AP/PA       #########
#################################################################

if not os.path.exists(os.path.join(source_dir,'nifti2')) and convert2bids:
	print('Running; BIDS formatting')
	bash_command = 'python generic_heudiconv_conhect.py'
	

########          group/session selection               #########

data_dir = os.path.join(source_dir,'nifti2','HealthyVolunteers')

layout = BIDSLayout(data_dir)


# Select subject and sessions

subject_list = layout.get_subjects()
session_list = layout.get_sessions()
dirs_list = layout.get_acquisitions()

print('Subjects : ', subject_list)
print('Sessions : ', session_list)
print('Aquisitions : ', dirs_list)

subject_list = ['02']
session_list = ['001']

CLI_subject_list = ','.join(subject_list)
CLI_session_list = ','.join(session_list)


#################################################################
#########         Tractography/Freesurfer pipeline    ###########
#################################################################

#from pipeline_parameters import * ici

if run_pipeline:
	command_pipeline = f'python 2_Tractography/multiple_wf.py {CLI_subject_list} {CLI_session_list}'
	subprocess.run(command_pipeline,shell = True)

#################################################################
#########        Create the connectivity matrixes      ##########
#################################################################

if createMatrixes:
	bash_command = f'python 3_MatrixesCreation/MatrixesCreation.py {CLI_subject_list} {CLI_session_list}'
	subprocess.run(bash_command,shell = True)

#################################################################
#########                 QA Check                     ##########
#################################################################

if QAcheck:
	bash_command = f'python QA_check/QA_check_nipype.py {CLI_subject_list} {CLI_session_list}'
	print(bash_command)
	subprocess.run(bash_command,shell = True)


if bundleSegmentation:
	bash_command = f'python 4_BundleSegmentation/BundleSegmentation.py {CLI_subject_list} {CLI_session_list}'
	print(bash_command)
	subprocess.run(bash_command,shell = True)

