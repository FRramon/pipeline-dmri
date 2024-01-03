# QA check for nipype pipeline

import subprocess
import os
import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from MatrixesCreationParameters import *

subject_raw = sys.argv[1]
session_raw = sys.argv[2]

subject_list = subject_raw.split(',')
ses_list = session_raw.split(',')

for sub in subject_list:

	for ses in ses_list:

		subject_id = 'sub-' + sub
		session_id = 'ses-' + ses
		identifier = '_ses_id_' + ses + '_subject_id_' + sub

		print(f"Running on {subject_id} - {session_id}")

		# Set directories
		main_workflow_dir = '/mnt/CONHECT_data/pipe_patients/main_workflow'
		preproc_dir = os.path.join(main_workflow_dir,'preproc',identifier)
		tracto_dir = os.path.join(main_workflow_dir,'wf_tractography',identifier)
		connectome_dir = os.path.join(main_workflow_dir,'connectome',identifier)


		if create_smallertck:
			bash_command = f'tckedit {tracto_dir}/tcksift2/sift_tracks.tck -number 100k {tracto_dir}/tcksift2/smaller100ktracks.tck'
			subprocess.run(bash_command,shell=True)

		#######################################################
		#####        	 Generate Connectome               ####
		#######################################################

		###### Create Mesh object for cortical & subcortical ROIs #####

		connectome_mesh_dir = os.path.join(connectome_dir,'mesh')
		if not os.path.exists(connectome_mesh_dir):
			os.mkdir(connectome_mesh_dir)

		if createMesh:
			bash_command = f'label2mesh {connectome_dir}/labelconvert/mapflow/_labelconvert2/parcellation.mif {connectome_mesh_dir}/mesh.obj -force'
			subprocess.run(bash_command,shell = True)


		#####				create SC matrix  				#####


		connectome_sc_dir = os.path.join(connectome_dir,'sc')
		if not os.path.exists(connectome_sc_dir):
			os.mkdir(connectome_sc_dir)

		if createSCmatrix:
			bash_command1 = f'tck2connectome –symmetric –zero_diagonal {tracto_dir}/tcksift2/sift_tracks.tck {connectome_dir}/labelconvert/mapflow/_labelconvert2/parcellation.mif {connectome_sc_dir}/sc_connectivity_matrix.csv –out_assignment {connectome_sc_dir}/sc_assignments.csv -force'
			print(f"Running command: {bash_command1}")
			subprocess.run(bash_command1,shell = True)

			bash_command2 = f'connectome2tck {tracto_dir}/tcksift2/sift_tracks.tck {connectome_sc_dir}/sc_assignments.csv {connectome_sc_dir}/exemplar_sc –files single –exemplars {connectome_dir}/labelconvert/mapflow/_labelconvert2/parcellation.mif -force'
			print(f"Running command: {bash_command2}")
			subprocess.run(bash_command2,shell = True)


		#####			create FA matrixes					####


		tracto_fa_dir = os.path.join(tracto_dir,'fa')
		if not os.path.exists(tracto_fa_dir):
			os.mkdir(tracto_fa_dir)

		connectome_fa_dir = os.path.join(connectome_dir,'fa')
		if not os.path.exists(connectome_fa_dir):
			os.mkdir(connectome_fa_dir)

		if createFAmatrix:
			# Create tensor
			bash_command = f'dwi2tensor -mask {tracto_dir}/brainmask/brainmask.mif {preproc_dir}/biascorrect/biascorrect.mif {tracto_dir}/fa/tensor.mif -force'
			subprocess.run(bash_command, shell=True)

			# Create FA map
			bash_command2 = f'tensor2metric {tracto_dir}/fa/tensor.mif -fa {tracto_dir}/fa/fa.mif -force'# | tensor2metric {tracto_dir}/fa/tensor.mif -vec {tracto_dir}/fa/vec.mif -force'
			subprocess.run(bash_command2, shell=True)

		 	# Create mean_FA_per_Streamline
			bash_command3 = f'tcksample {tracto_dir}/tcksift2/sift_tracks.tck {tracto_dir}/fa/fa.mif {connectome_dir}/fa/mean_FA_per_streamline.csv -stat_tck mean -force'
			subprocess.run(bash_command3, shell=True)

		 	# Create FA matrix
			bash_command4 = f'tck2connectome -symmetric -zero_diagonal {tracto_dir}/tcksift2/sift_tracks.tck {connectome_dir}/labelconvert/mapflow/_labelconvert2/parcellation.mif {connectome_dir}/fa/fa_connectivity_matrix.csv -scale_file {connectome_dir}/fa/mean_FA_per_streamline.csv -stat_edge mean –out_assignment {connectome_dir}/fa/fa_assignments.csv -force'
			subprocess.run(bash_command4,shell = True)

		    # Create streamtubes
			bash_command = f'connectome2tck {tracto_dir}/tcksift2/sift_tracks.tck {connectome_fa_dir}/fa_assignments.csv {connectome_fa_dir}/exemplar_fa –files single –exemplars {connectome_dir}/labelconvert/mapflow/_labelconvert2/parcellation.mif -force'
			subprocess.run(bash_command,shell = True)

		if save_matrix:
			sc_file_path = f'{connectome_sc_dir}/sc_connectivity_matrix.csv'   
			fa_file_path = f'{connectome_fa_dir}/fa_connectivity_matrix.csv'   


			if not (os.path.isfile(sc_file_path) and os.path.isfile(fa_file_path)):
			    print("Error: One or more files not found.")
			    sys.exit(1)

			# Read the CSV files without skipping the header

			df_sc = pd.read_csv(sc_file_path, header=None)
			df_fa = pd.read_csv(fa_file_path, header=None)

			# Calculate the adaptive outlier threshold (e.g., 99th percentile) for both dataframes
			outlier_threshold_sc = df_sc.stack().quantile(0.99)
			outlier_threshold_fa = 1

			# Create a function to generate and save the heatmap
			def save_heatmap(dataframe,outlier_threshold,label):
			    plt.figure(figsize=(10, 8))
			    sns.heatmap(dataframe, cmap='viridis', vmin=0, vmax=outlier_threshold, annot = False, fmt=".2f")
			    plt.title(f' sub-{sub} - ses-{ses} - {label}')
			   

			    # Save the heatmap as a PNG file in the source data folder
			    
			    output_file_path = f'{connectome_dir}/{label}/{label}_connectivity_matrix.png'
			    plt.savefig(output_file_path)

			    # Show the plot (optional)
			    #plt.show()

			# Save the first heatmap
			save_heatmap(df_sc,outlier_threshold_sc, "sc")

			# Save the second heatmap
			save_heatmap(df_fa,outlier_threshold_fa, "fa")


		if viewSCConnectome:
			bash_command = f'mrview {preproc_dir}/biascorrect/biascorrect.mif -connectome.init {connectome_dir}/labelconvert/mapflow/_labelconvert2/parcellation.mif -connectome.load {connectome_sc_dir}/sc_connectivity_matrix.csv -imagevisible 0'
			subprocess.run(bash_command,shell = True)

		if viewFAConnectome:
			bash_command = f'mrview {preproc_dir}/biascorrect/biascorrect.mif -connectome.init {connectome_dir}/labelconvert/mapflow/_labelconvert2/parcellation.mif -connectome.load {connectome_fa_dir}/fa_connectivity_matrix.csv -imagevisible 0'
			subprocess.run(bash_command,shell = True)



# if viewFA:
# 	bash_command = f'mrview {tracto_dir}/fa/fa.mif'
# 	subprocess.run(bash_command,shell=True)


### Bundle identification...
### Partir du principe que SIFT2 a été faite+ labelconvert + tck2connectome SC
# Il faut faire la partie FA à la main.

## Les assignments sont spécifique au label convert donc peut être essayer de les créer automatiquement avec le mapnode.

#
