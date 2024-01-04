import os
import subprocess
from bids.layout import BIDSLayout

from tractography_utils import *
from run_parameters import *


#################################################################
#########         BIDS Formatting & Correct AP/PA       #########
#################################################################

# if not os.path.exists(os.path.join(source_dir,'nifti3')) and convert2bids:
# 	print('Running; BIDS formatting')
# 	bash_command = 'python generic_heudiconv_conhect.py'
	

########          group/session selection               #########


data_dir = os.path.join(source_dir,data_folder,group)
base_directory = source_dir + '/' + pipe_name
out_dir = source_dir + '/' + result_name


# Select subject and sessions
layout = BIDSLayout(data_dir)
# subject_list = layout.get_subjects()
# session_list = layout.get_sessions()
# dirs_list = layout.get_acquisitions()

# print('Subjects : ', subject_list)
# print('Sessions : ', session_list)
# print('Aquisitions : ', dirs_list)



subject_list = get_list_sessions(source_dir,group,session_list[0])


CLI_subject_list = ','.join(subject_list)
CLI_session_list = ','.join(session_list)


#################################################################
#########         Tractography/Freesurfer pipeline    ###########
#################################################################

#from pipeline_parameters import * ici

if run_pipeline:
	# command_pipeline10 = f'python 2_Tractography/multiple_wf.py {CLI_subject_list} {CLI_session_list} {pipe_name10} {result_name10} {ntracks10}'
	# subprocess.run(command_pipeline10,shell = True)
	# command_pipeline20 = f'python 2_Tractography/multiple_wf.py {CLI_subject_list} {CLI_session_list} {pipe_name20} {result_name20} {ntracks20}'
	# subprocess.run(command_pipeline20,shell = True)
	command_pipeline30 = f'python 2_Tractography/multiple_wf.py {data_dir} {CLI_subject_list} {CLI_session_list} {base_directory} {out_dir} {ntracks} '
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

