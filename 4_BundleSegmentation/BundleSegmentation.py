# Bundle Segmentation

import subprocess
#######################################################################################
###                 Bundle Segmentation based on CSD in MNI space                  ####
#######################################################################################

import os
import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

#from BundleSegmentationParameters import *

subject_raw = sys.argv[1]
session_raw = sys.argv[2]

subject_list = subject_raw.split(',')
ses_list = session_raw.split(',')

mni_file='/home/francoisramon/miniconda3/lib/python3.11/site-packages/tractseg/resources/MNI_FA_template.nii.gz'
b=False
c=False
d=False
d2 = False
e2 = False
e = False
e3 = True
f2 = True
f = False

for sub in subject_list:

	for ses in ses_list:


		subject_id = 'sub-' + sub
		session_id = 'ses-' + ses
		identifier = '_ses_id_' + ses + '_subject_id_' + sub

		print(f"Running on {subject_id} - {session_id}")


		# Set directories
		main_workflow_dir = '/mnt/CONHECT_data/pipe_healthy/main_workflow'
		dwi_dir = os.path.join(main_workflow_dir,'wf_dc',identifier,'mrconvertPA','mapflow')
		tracto_dir = os.path.join(main_workflow_dir,'wf_tractography',identifier)
		freesurfer_dir = os.path.join(main_workflow_dir,'fs_workflow',identifier,'fs_reconall',sub,'mri')

		raw_dir = os.path.join(main_workflow_dir,'bundle_segmentation')
		if not os.path.exists(raw_dir):
			os.mkdir(raw_dir)

		bundle_dir = os.path.join(raw_dir,identifier)
		if not os.path.exists(bundle_dir):
			os.mkdir(bundle_dir)

		dwimif = bundle_dir + '/DWI.mif'
		if not os.path.isfile(dwimif):
			print('Concatenating dwis')
			command_cat = f'dwicat {dwi_dir}/_mrconvertPA0/dwi.mif {dwi_dir}/_mrconvertPA1/dwi.mif {dwi_dir}/_mrconvertPA2/dwi.mif {bundle_dir}/DWI.mif -force'
			subprocess.run(command_cat, shell = True)

		
		dwinii = bundle_dir + '/DWI.nii.gz'
		if not os.path.exists(dwinii):
			print('Convert dwi to nifti')
			command_convert_dwi = f'mrconvert {bundle_dir}/DWI.mif {bundle_dir}/DWI.nii.gz -export_grad_fsl {bundle_dir}/bvec.bvecs {bundle_dir}/bval.bvals -force'
			subprocess.run(command_convert_dwi, shell = True)
		
		masknii = bundle_dir + '/brainmask.nii.gz'
		if not os.path.exists(masknii):
			print('Convert Mask to nifti')
			command_convert_mask = f'mrconvert {main_workflow_dir}/wf_tractography/{identifier}/brainmask/brainmask.mif {bundle_dir}/brainmask.nii.gz -force'
			subprocess.run(command_convert_mask, shell = True)

		FAnii = bundle_dir + '/FA.nii.gz'
		if not os.path.exists(FAnii):
			print('Computing FA for MNI registration')
			command_calcFA = f'calc_FA -i {bundle_dir}/DWI.nii.gz -o {bundle_dir}/FA.nii.gz --bvals {bundle_dir}/bval.bvals --bvecs {bundle_dir}/bvec.bvecs --brain_mask {bundle_dir}/brainmask.nii.gz'
			subprocess.run(command_calcFA, shell = True)

		FAMNInii = bundle_dir + '/FA_MNI.nii.gz'
		if not os.path.isfile(FAMNInii):
			print('Computing flirt mat for MNI registration')
			command_calcFA = f'flirt -ref {mni_file} -in {bundle_dir}/FA.nii.gz -out {bundle_dir}/FA_MNI.nii.gz -omat {bundle_dir}/FA_2_MNI.mat -dof 6 -cost mutualinfo -searchcost mutualinfo'
			subprocess.run(command_calcFA, shell = True)

		diffusion_mni_nii = bundle_dir + '/Diffusion_MNI.nii.gz'
		if not os.path.isfile(diffusion_mni_nii):
			print('apply transformation MNI registration on dwi')
			command_1 = f'flirt -ref {mni_file} -in {bundle_dir}/DWI.nii.gz -out {bundle_dir}/Diffusion_MNI.nii.gz -applyxfm -init {bundle_dir}/FA_2_MNI.mat -dof 6'
			subprocess.run(command_1, shell = True)

			command_2 = f'cp {bundle_dir}/bval.bvals {bundle_dir}/MNI_bval.bvals'
			subprocess.run(command_2, shell = True)

			command_3 = f'rotate_bvecs -i {bundle_dir}/bvec.bvecs -t {bundle_dir}/FA_2_MNI.mat -o {bundle_dir}/MNI_bvec.bvecs'
			subprocess.run(command_3, shell = True)

		output = os.path.join(bundle_dir,'tractseg_output')
		# if not os.path.exists(output):
		# 	print('apply TractSeg')
		# 	command = f'TractSeg -i {bundle_dir}/Diffusion_MNI.nii.gz -o {bundle_dir}/tractseg_output --output_type tract_segmentation --raw_diffusion_input --bvals {bundle_dir}/MNI_bval.bvals --bvecs {bundle_dir}/MNI_bvec.bvecs --csd_type csd_msmt --super_resolution'
		# 	subprocess.run(command,shell = True)


		if b:
			command = f'convert_xfm -omat {bundle_dir}/MNI_2_FA.mat -inverse {bundle_dir}/FA_2_MNI.mat'
			subprocess.run(command,shell = True)

		if c:
			bundles_MNI = os.listdir(os.path.join(output,'bundle_segmentations'))
			segMNI = os.path.join(output,'bundle_segmentations')
			#segPatient = os.mkdir(os.path.join(output,'segmentation_subject_space'))
			segPatient = os.path.join(output,'segmentation_subject_space')
			for bundles in bundles_MNI:
				print(bundles)
				command = f'flirt -ref {bundle_dir}/FA.nii.gz -in {segMNI}/{bundles} -out {segPatient}/subject_space_{bundles} -applyxfm -init {bundle_dir}/MNI_2_FA.mat -dof 6 -interp spline'
				subprocess.run(command,shell=True)

		if d:
			print('mask streamlines into bundle')
			bundles_patients = os.listdir(os.path.join(output,'segmentation_subject_space'))
			#segPatient = os.path.join(output,'bundle_segmentations')
			#segPatient = os.mkdir(os.path.join(output,'segmentation_subject_space'))
			segPatient = os.path.join(output,'segmentation_subject_space')
			#tracts_subject = os.mkdir(os.path.join(output,'tracts_subject'))
			tracts_subject= os.path.join(output,'tracts_subject')
			for bundles in bundles_patients:
			
				tract_name = bundles[:-7] + '.tck'
				#print(tract_name)
				command = f'tckedit -mask {segPatient}/{bundles} {tracto_dir}/tcksift2/sift_tracks.tck {tracts_subject}/{tract_name} -force'
				print(command)
				subprocess.run(command,shell=True)

		if d2:
			print('mask streamlines into bundle')
			bundles_patients = os.listdir(os.path.join(output,'segmentation_subject_space'))
			#segPatient = os.path.join(output,'bundle_segmentations')
			#os.mkdir(os.path.join(output,'segmentation_subject_space_inverse'))
			segPatient = os.path.join(output,'segmentation_subject_space')
			segInverse = os.path.join(output,'segmentation_subject_space_inverse')
			for bundles in bundles_patients:
				tract_name = bundles[14:-7] + '.mif'
				#print(tract_name)
				command = f'mrthreshold {segPatient}/{bundles} -invert {segInverse}/{tract_name} -force'
				print(command)
				subprocess.run(command,shell=True)


		if e2:
			print('mask streamlines into bundle - with exclude')
			bundles_patients = os.listdir(os.path.join(output,'segmentation_subject_space_inverse'))
			#segPatient = os.path.join(output,'bundle_segmentations')
			#segPatient = os.mkdir(os.path.join(output,'segmentation_subject_space'))
			segInverse = os.path.join(output,'segmentation_subject_space_inverse')
			#os.mkdir(os.path.join(output,'tracts_subject_2'))
			tracts_subject= os.path.join(output,'tracts_subject_2')
			for bundles in bundles_patients:
			
				tract_name = bundles[:-4] + '.tck'
				#print(tract_name)
				command = f'tckedit -exclude {segInverse}/{bundles} {tracto_dir}/tcksift2/sift_tracks.tck {tracts_subject}/{tract_name} -force'
				print(command)
				subprocess.run(command,shell=True)


		if e3:
			print('filter to 3k fibres')
			tracts_list = os.listdir(os.path.join(output,'tracts_subject_2'))
		
			#segInverse = os.path.join(output,'segmentation_subject_space_inverse')
		
			tracts_subject= os.path.join(output,'tracts_subject_2')


			os.mkdir(os.path.join(output,'5k_tracts'))
			tracts_3k_dir = os.path.join(output,'5k_tracts')

			for tracts in tracts_list:
			
				#tract_name = bundles[:-4] + '.tck'
				#print(tract_name)
				command = f'tckedit  {tracts_subject}/{tracts} -number 5k {tracts_3k_dir}/3k_{tracts} -force'
				print(command)
				subprocess.run(command,shell=True)


		if e:
			print('Viewing whole segmentation')
			
			tracts_subject= os.path.join(output,'tracts_subject')
			tracts_list = os.listdir(tracts_subject)

			command = f'mrview {freesurfer_dir}/brain.mgz '
			for tracts in tracts_list:

				R = np.random.choice(range(256))
				G = np.random.choice(range(256))
				B = np.random.choice(range(256))

		
				command_i = f'-tractography.load {tracts_subject}/{tracts} -tractography.geometry lines -tractography.colour {R},{G},{B} -tractography.opacity 1 ' 
				command += command_i

			#print(command)
			subprocess.run(command,shell = True)


		if f2:
			print('Viewing whole segmentation 2')
			
			tracts_subject= os.path.join(output,'5k_tracts')
			tracts_list = os.listdir(tracts_subject)

			command = f'mrview {freesurfer_dir}/brain.mgz '
			for tracts in tracts_list:

				R = np.random.choice(range(256))
				G = np.random.choice(range(256))
				B = np.random.choice(range(256))

		
				command_i = f'-tractography.load {tracts_subject}/{tracts} -tractography.geometry lines -tractography.colour {R},{G},{B} -tractography.opacity 1 ' 
				command += command_i

			#print(command)
			subprocess.run(command,shell = True)





		if f:
			print('Viewing whole segmentation tractseg')
			
			tracts_seg= os.path.join(output,'TOM_trackings')
			tracts_list = os.listdir(tracts_seg)

			command = f'mrview {bundle_dir}/FA_MNI.nii.gz '
			for tracts in tracts_list:

				R = np.random.choice(range(256))
				G = np.random.choice(range(256))
				B = np.random.choice(range(256))

		
				command_i = f'-tractography.load {tracts_seg}/{tracts} -tractography.geometry pseudotubes -tractography.colour {R},{G},{B} -tractography.opacity 1 ' 
				command += command_i

			#print(command)
			subprocess.run(command,shell = True)


### Ajouter TractSeg -i /mnt/CONHECT_data/pipe_healthy/main_workflow/bundle_segmentation/_ses_id_001_subject_id_02/tractseg_output/peaks.nii.gz -o /mnt/CONHECT_data/pipe_healthy/main_workflow/bundle_segmentation/_ses_id_001_subject_id_02/tractseg_output --output_type endings_segmentation



### Ajouter TractSeg -i /mnt/CONHECT_data/pipe_healthy/main_workflow/bundle_segmentation/_ses_id_001_subject_id_02/tractseg_output/peaks.nii.gz -o /mnt/CONHECT_data/pipe_healthy/main_workflow/bundle_segmentation/_ses_id_001_subject_id_02/tractseg_output --output_type TOM






		
		

		








		


