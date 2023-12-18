import subprocess
import os
import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from QA_check_parameters import *

arg1 = sys.argv[1]
arg2 = sys.argv[2]

subject_list = arg1.split(',')
ses_list = arg2.split(',')

print(subject_list)
print(ses_list)

for sub in subject_list:

	for ses in ses_list:

		subject_id = 'sub-' + sub
		session_id = 'ses-' + ses
		identifier = '_ses_id_' + ses + '_subject_id_' + sub

		print(f"Running on {subject_id} - {session_id}")

		# Set directories
		main_workflow_dir = '/mnt/CONHECT_data/pipe_healthy/main_workflow'
		preproc_dir = os.path.join(main_workflow_dir,'preproc',identifier)
		tracto_dir = os.path.join(main_workflow_dir,'wf_tractography',identifier)
		connectome_dir = os.path.join(main_workflow_dir,'connectome',identifier)

		#######################################################
		#####         View preprocessing steps             ####
		#######################################################

		# View denoised DWI + unr
		if view_denoised:
			bash_command = f"mrview {preproc_dir}/unring/concatenated_denoised_unr.mif -mode 2"
			print(f"Running command: {bash_command}")
			# Run the Bash script using subprocess
			subprocess.run(bash_command, shell=True)

		# # Overlay b=0 AP and PA
		if view_b0:
			bash_command = f"mrview {preproc_dir}/avg_b0PA/avg_b0PA.mif -overlay.load {preproc_dir}/b0AP_extract/b0AP.mif -overlay.opacity 0.3 -overlay.colourmap 2 -mode 2"
			print(f"Running command: {bash_command}")
			# Run the Bash script using subprocess
			subprocess.run(bash_command, shell=True)

		# View overlay of DWI preprocessed and denoised
		if view_preproc:
			bash_command = f"mrview {preproc_dir}/unring/concatenated_denoised_unr.mif -overlay.load {preproc_dir}/biascorrect/biascorrect.mif -overlay.opacity 0.3 -overlay.colourmap 2 -mode 2"
			print(f"Running command: {bash_command}")
			# Run the Bash script using subprocess
			subprocess.run(bash_command, shell=True)

		######################################################
		#####        View coregistration           ###########
		######################################################

		if view_avgb0:
			bash_command = f"mrview {tracto_dir}/avg_b0/avg_b0.mif -mode 2"
			print(f"Running command: {bash_command}")
			# Run the Bash script using subprocess
			subprocess.run(bash_command, shell=True)
			
		if view_registration:
			bash_command = f"mrview {preproc_dir}/biascorrect/biascorrect.mif -overlay.load {tracto_dir}/transformT1/T1_coreg.mif -overlay.opacity 0.3 -overlay.colourmap 2 -mode 2"
			print(f"Running command: {bash_command}")
			# Run the Bash script using subprocess
			subprocess.run(bash_command, shell=True)

		#######################################################
		#####         View orientation dispersion          ####
		#######################################################

		# View 5 tissue segmentation (press right)
		if view_5tt:
			bash_command = f"mrview {tracto_dir}/gen5tt/5tt.mif -mode 2"
			print(f"Running command: {bash_command}")
			# Run the Bash script using subprocess
			subprocess.run(bash_command, shell=True)

		# Creer vf.mi
		if create_vf:
			bash_command = f"mrconvert --coord 3 0 {tracto_dir}/dwi2fod/wm.mif - | mrcat {tracto_dir}/dwi2fod/csf.mif {tracto_dir}/dwi2fod/gm.mif - {tracto_dir}/dwi2fod/vf.mif -force"
			print(f"Running command: {bash_command}")
			# Run the Bash script using subprocess
			subprocess.run(bash_command, shell=True)

		# View ODF over tissue segmentation
		if view_odf:
			bash_command = f"mrview {tracto_dir}/dwi2fod/vf.mif -odf.load_sh {tracto_dir}/dwi2fod/wm.mif -mode 2"
			print(f"Running command: {bash_command}")
			# Run the Bash script using subprocess
			subprocess.run(bash_command, shell=True)

		#######################################################
		#####         View tractography steps             ####
		#######################################################

		# changer pour avoir le sift --> 200k
		# Create a smaller file for tractography 
		if create_smallertck:
			bash_command = f"tckedit {tracto_dir}/tckgen/tracked.tck -number 200k {tracto_dir}/tckgen/smaller200ktracks.tck -force"
			print(f"Running command: {bash_command}")
			# Run the Bash script using subprocess
			subprocess.run(bash_command, shell=True)

		# View tractography
		if view_streamline:
			bash_command = f"mrview {preproc_dir}/biascorrect/biascorrect.mif -tractography.load {tracto_dir}/tckgen/smaller200ktracks.tck -mode 2"
			print(f"Running command: {bash_command}")
			# Run the Bash script using subprocess
			subprocess.run(bash_command, shell=True)

		#######################################################
		#####         View Freesurfer Parcellation         ####
		#######################################################

		# Freesurfer directory
		reconall_dir = os.path.join(main_workflow_dir,'fs_workflow',identifier,'fs_reconall',sub)

		# View freesurfer segmentation - Destrieux Atlas
		if view_freesurfer:
			bash_command = f"freeview {reconall_dir}/mri/aparc.a2009s+aseg.mgz"
			print(f"Running command: {bash_command}")
			subprocess.run(bash_command, shell=True)



