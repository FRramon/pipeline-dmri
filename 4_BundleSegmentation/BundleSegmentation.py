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

from BundleSegmentationParameters import *

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
			print('--- [Node] : Concatenating DWIs')
			command_cat = f'dwicat {dwi_dir}/_mrconvertPA0/dwi.mif {dwi_dir}/_mrconvertPA1/dwi.mif {dwi_dir}/_mrconvertPA2/dwi.mif {bundle_dir}/DWI.mif -force'
			subprocess.run(command_cat, shell = True)
		elif verbose == True: 
			print('--- [Node] : DWI concatenation already done')
		
		dwinii = bundle_dir + '/DWI.nii.gz'
		if not os.path.isfile(dwinii):
			print('--- [Node] : Convert dwi to nifti')
			command_convert_dwi = f'mrconvert {bundle_dir}/DWI.mif {bundle_dir}/DWI.nii.gz -export_grad_fsl {bundle_dir}/bvec.bvecs {bundle_dir}/bval.bvals -force'
			subprocess.run(command_convert_dwi, shell = True)
		elif verbose == True: 
			print('--- [Node] : DWI conversion from mif to nifti already done')
		
		masknii = bundle_dir + '/brainmask.nii.gz'
		if not os.path.isfile(masknii):
			print('--- [Node] : Convert Mask to nifti')
			command_convert_mask = f'mrconvert {main_workflow_dir}/wf_tractography/{identifier}/brainmask/brainmask.mif {bundle_dir}/brainmask.nii.gz -force'
			subprocess.run(command_convert_mask, shell = True)
		elif verbose == True: 
			print('--- [Node] : Mask conversion to nifti already done')

		FAnii = bundle_dir + '/FA.nii.gz'
		if not os.path.isfile(FAnii):
			print('--- [Node] : Computing FA for MNI registration')
			command_calcFA = f'calc_FA -i {bundle_dir}/DWI.nii.gz -o {bundle_dir}/FA.nii.gz --bvals {bundle_dir}/bval.bvals --bvecs {bundle_dir}/bvec.bvecs --brain_mask {bundle_dir}/brainmask.nii.gz'
			subprocess.run(command_calcFA, shell = True)
		elif verbose == True: 
			print('--- [Node] : FA already computed')

		FAMNInii = bundle_dir + '/FA_MNI.nii.gz'
		if not os.path.isfile(FAMNInii):
			print('--- [Node] : Computing flirt mat for MNI registration')
			command_calcFA = f'flirt -ref {mni_file} -in {bundle_dir}/FA.nii.gz -out {bundle_dir}/FA_MNI.nii.gz -omat {bundle_dir}/FA_2_MNI.mat -dof 6 -cost mutualinfo -searchcost mutualinfo'
			subprocess.run(command_calcFA, shell = True)
		elif verbose == True: 
			print('--- [Node] : MNI registration already applied to FA')

		diffusion_mni_nii = bundle_dir + '/Diffusion_MNI.nii.gz'
		if not os.path.isfile(diffusion_mni_nii):
			print('--- [Node] : Apply transformation MNI registration on dwi')
			command_1 = f'flirt -ref {mni_file} -in {bundle_dir}/DWI.nii.gz -out {bundle_dir}/Diffusion_MNI.nii.gz -applyxfm -init {bundle_dir}/FA_2_MNI.mat -dof 6'
			subprocess.run(command_1, shell = True)

			command_2 = f'cp {bundle_dir}/bval.bvals {bundle_dir}/MNI_bval.bvals'
			subprocess.run(command_2, shell = True)

			command_3 = f'rotate_bvecs -i {bundle_dir}/bvec.bvecs -t {bundle_dir}/FA_2_MNI.mat -o {bundle_dir}/MNI_bvec.bvecs'
			subprocess.run(command_3, shell = True)
		elif verbose == True: 
			print('--- [Node] : MNI registration already applied to DWI')


		outputdir = bundle_dir + '/tractseg_output'
		if not os.path.exists(outputdir):
			print('--- [Node] : Creating output directory')
			os.mkdir(outputdir)
		elif verbose == True: 
			print('--- [Node] : /tractseg_output directory already created  ')

		
		segdir = outputdir + '/bundle_segmentations'
		if not os.path.exists(segdir):
			os.mkdir(segdir)
			print('apply TractSeg')
			command = f'TractSeg -i {bundle_dir}/Diffusion_MNI.nii.gz -o {bundle_dir}/tractseg_output --output_type tract_segmentation --raw_diffusion_input --bvals {bundle_dir}/MNI_bval.bvals --bvecs {bundle_dir}/MNI_bvec.bvecs --csd_type csd_msmt --super_resolution'
			subprocess.run(command,shell = True)

			# command_rm = f'rm {segdir}/.tck'
			# subprocess.run(command_rm,shell = True)
		elif verbose == True: 
			print('--- [Node] : Tractseg already segmented bundle volumes')	


		mni2fa = bundle_dir + '/MNI_2_FA.mat'
		if not os.path.isfile(mni2fa):
			command = f'convert_xfm -omat {bundle_dir}/MNI_2_FA.mat -inverse {bundle_dir}/FA_2_MNI.mat'
			print(command)
			subprocess.run(command,shell = True)
		elif verbose == True: 
			print('--- [Node] : MNI to FA registration  matrix already created')	
		

		segSubject = outputdir + '/segmentation_subject_space'
		if not os.path.exists(segSubject):
			os.mkdir(segSubject)
			print('--- [Node] : Moving bundles masks to subject space')
			bundles_MNI = os.listdir(os.path.join(output,'bundle_segmentations'))
			
			for bundles in bundles_MNI:
				if verbose: print(f'Moving {bundles} to subject space')
				command = f'flirt -ref {bundle_dir}/FA.nii.gz -in {segdir}/{bundles} -out {segSubject}/subject_space_{bundles} -applyxfm -init {bundle_dir}/MNI_2_FA.mat -dof 6 -interp spline'
				subprocess.run(command,shell=True)
		elif verbose == True:
			print('--- [Node] : Bundles already transformed to subject space')



		segInverse = outputdir + '/segmentation_subject_space_inverse'
		if not os.path.exists(segInverse):
			os.mkdir(segInverse)
			print('--- [Node] : Inversing pixels in bundle masks')
			bundles_subject = os.listdir(segSubject)
			for bundles in bundles_subject:
				if verbose: print(f'	--- Inversing {bundles}')
				tract_name = bundles[14:-7] + '.mif'
				command = f'mrthreshold {segSubject}/{bundles} -invert {segInverse}/{tract_name} -force'
				subprocess.run(command,shell=True)
		elif verbose == True:
			print('--- [Node] : Bundle mask already inverted')


		tracts_subject_masked = outputdir + '/tracts_subject_masked'
		if not os.path.exists(tracts_subject_masked):
			os.mkdir(tracts_subject_masked)
			print('--- [Node] : mask streamlines into bundle - with exclude')
			bundles_subject = os.listdir(segInverse)
			for bundles in bundles_subject:
				if verbose: print(f'	--- masking {bundles}')
				tract_name = bundles[:-4] + '.tck'
				command = f'tckedit -exclude {segInverse}/{bundles} {tracto_dir}/tcksift2/sift_tracks.tck {tracts_subject_masked}/{tract_name} -force'
				print(command)
				subprocess.run(command,shell=True)
		elif verbose == True:
			print('--- [Node] : masking streamlines into bundles by exclusion already done')


		tracts_5k = outputdir + '/tracts_5k'
		if not os.path.exists(tracts_5k):
			os.mkdir(tracts_5k)
			print('--- [Node] : filter to 5k fibres')
			tracts_list = os.listdir(tracts_subject_masked)
			for tracts in tracts_list:
				command = f'tckedit  {tracts_subject_masked}/{tracts} -number 5k {tracts_5k}/5k_{tracts} -force'
				print(command)
				subprocess.run(command,shell=True)
		elif verbose == True:
			print('--- [Node] : Filtering to 5k fibers per bundle for visualization already done')


		if ViewAllTracts:
			print('--- [Node] : Viewing whole 5k segmentation')
			
			tracts_list = os.listdir(tracts_subject_masked)

			command = f'mrview {freesurfer_dir}/brain.mgz '
			for tracts in tracts_list:

				R = np.random.choice(range(256))
				G = np.random.choice(range(256))
				B = np.random.choice(range(256))

		
				command_i = f'-mode 3 -imagevisible 0 -tractography.load {tracts_subject_masked}/{tracts} -tractography.geometry pseudotubes -tractography.colour {R},{G},{B} -tractography.opacity 1 ' 
				command += command_i

			#print(command)
			subprocess.run(command,shell = True)


		if View5kTracts:
			print('--- [Node] : Viewing whole segmentation ')
			
			
			tracts_list = os.listdir(tracts_5k)

			command = f'mrview {freesurfer_dir}/brain.mgz '
			for tracts in tracts_list:

				R = np.random.choice(range(256))
				G = np.random.choice(range(256))
				B = np.random.choice(range(256))

		
				command_i = f' -mode 3 -imagevisible 0 -tractography.load {tracts_5k}/{tracts} -tractography.geometry pseudotubes -tractography.thickness 0.1 -tractography.colour {R},{G},{B} -tractography.opacity 1' 
				command += command_i

			#print(command)
			subprocess.run(command,shell = True)



		if ViewTractSegTracts:
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






		
		

		








		


