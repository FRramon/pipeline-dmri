import os
import subprocess
from bids.layout import BIDSLayout

######                    Instructions                   #######

convert2bids = False
run_pipeline = True

createMatrixes = False
createROIfile = False
QAcheck = False
bundleSegmentation= False
ClusterConsensus = False

source_dir = '/mnt/CONHECT_data'

pipe_name10 = 'pipe_patients_10'
result_name10 = 'results_patients_10'
ntracks10 = 10000000

pipe_name20 = 'pipe_patients_20'
result_name20 = 'results_patients_20'
ntracks20 = 20000000

pipe_name30 = 'pipe_patients_30'
result_name30 = 'results_patients_30'
ntracks30 = 30000000

#################################################################
#########         BIDS Formatting & Correct AP/PA       #########
#################################################################

if not os.path.exists(os.path.join(source_dir,'nifti2')) and convert2bids:
	print('Running; BIDS formatting')
	bash_command = 'python generic_heudiconv_conhect.py'
	

########          group/session selection               #########
group = 'Patients'
data_dir = os.path.join(source_dir,'nifti2',group)

layout = BIDSLayout(data_dir)

# Select subject and sessions

subject_list = layout.get_subjects()
session_list = layout.get_sessions()
dirs_list = layout.get_acquisitions()

print('Subjects : ', subject_list)
print('Sessions : ', session_list)
print('Aquisitions : ', dirs_list)


### Ajouter une fonction qui vient chercher les numéros des patients qui ont une session 001,002 ou 003 selon ce qui est voulu

subject_list = ['01,02,03,04,05,06,07,08,09']#12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45']
session_list = ['001']


CLI_subject_list = ','.join(subject_list)
CLI_session_list = ','.join(session_list)


#################################################################
#########         Tractography/Freesurfer pipeline    ###########
#################################################################

#from pipeline_parameters import * ici

if run_pipeline:
	command_pipeline10 = f'python 2_Tractography/multiple_wf.py {CLI_subject_list} {CLI_session_list} {pipe_name10} {result_name10} {ntracks10}'
	subprocess.run(command_pipeline10,shell = True)
	command_pipeline20 = f'python 2_Tractography/multiple_wf.py {CLI_subject_list} {CLI_session_list} {pipe_name20} {result_name20} {ntracks20}'
	subprocess.run(command_pipeline20,shell = True)
	command_pipeline30 = f'python 2_Tractography/multiple_wf.py {CLI_subject_list} {CLI_session_list} {pipe_name30} {result_name30} {ntracks30} '
	subprocess.run(command_pipeline30,shell = True)


#################################################################
#########        Create the connectivity matrixes      ##########
#################################################################


if createMatrixes:
	bash_command = f'python 3_MatrixesCreation/MatrixesCreation.py {CLI_subject_list} {CLI_session_list}'
	subprocess.run(bash_command,shell = True)
	

if createROIfile:
	bash_command = f'python 3_MatrixesCreation/createROIfile.py {CLI_subject_list} {CLI_session_list} {group} {source_dir}'
	subprocess.run(bash_command,shell = True)

#################################################################
#########                 QA Check                     ##########
#################################################################

if QAcheck:
	bash_command = f'python QA_check/QA_check_nipype.py {CLI_subject_list} {CLI_session_list}'
	print(bash_command)
	subprocess.run(bash_command,shell = True)


if bundleSegmentation:
	bash_command = f'python 4_BundleSegmentation/BundleSegmentation.py {CLI_subject_list} {CLI_session_list} {source_dir}'
	print(bash_command)
	subprocess.run(bash_command,shell = True)

if ClusterConsensus:
	bash_command = f'python NetworkAnalysis/ClusterConsensus.py {CLI_subject_list} {CLI_session_list} {source_dir}'
	print(bash_command)
	subprocess.run(bash_command,shell = True)

