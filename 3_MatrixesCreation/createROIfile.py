#################################################
####            Create ROI to ROI file       ####
#################################################


import os
import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import subprocess

group_raw = sys.argv[3]
source_dir = sys.argv[4]

subject_raw = sys.argv[1]
session_raw = sys.argv[2]

subject_list = subject_raw.split(',')
ses_list = session_raw.split(',')

if group_raw == 'HealthyVolunteers':
	result_dir = os.path.join(source_dir , 'results_test2')
elif group_raw == 'Patients':
	result_dir = os.path.join(source_dir , 'pipe_patients')
elif group_raw == 'Controls':
	result_dir = os.path.join(source_dir , 'pipe_controls')

all_non_zero_entries = []


for sub in subject_list:

	ses_dir = os.path.join(result_dir,f'sub-{sub}')


	#sessions = os.listdir(ses_dir)

	for ses in ses_list:
		connectome_dir = os.path.join(ses_dir, f'ses-{ses}','5_Connectome')
		print(connectome_dir)
		if not os.path.exists(connectome_dir):
			sys.exit(
				f'Error File not Found: Pipeline has not created connectome matrix for {sub} on {ses}')
		else:
			print(f'RUNNING : {sub} - {ses}')

			print(f'--- Creating ROI file')
			input_file = os.path.join(connectome_dir, 'connectome.csv')

			df = pd.read_csv(input_file)
			# Create a list to store the non-zero entries for each subject and session
			non_zero_entries = []
			for i in range(df.shape[0]):
				for j in range(df.shape[1]):
					if df.iloc[i, j] != 0 and i != 0 and j != 0:
						non_zero_entries.append({'subject': sub, 'session': ses, 'i': i, 'j': j, 'FiberCount': df.iloc[i, j]})

			# Extend the list of all_non_zero_entries with the current subject and session entri
			
			current_df = pd.DataFrame(non_zero_entries)

            # Print the sum of the 'k' column for the current subject and session
			print(f"Sum of fibercount for {sub} on {ses}: {current_df['FiberCount'].sum()}")

			print(f"--- Add cortical zones labels to roi file")

			input_file = source_dir + '/code/fs_a2009s.txt'
			df_labelconvert = pd.read_csv(input_file,delim_whitespace = True, comment = '#',header=None, names=['index', 'labelname', 'R', 'G', 'B', 'A'])

			df_withlabels = pd.merge(current_df, df_labelconvert[['index', 'labelname']], left_on='i', right_on='index', how='left')
			df_withlabels.rename(columns={'labelname': 'ROI1'}, inplace=True)
			df_withlabels.drop(columns='index', inplace=True)

			# Merge again for 'j' to get ROI2
			df_withlabels = pd.merge(df_withlabels, df_labelconvert[['index', 'labelname']], left_on='j', right_on='index', how='left')
			df_withlabels.rename(columns={'labelname': 'ROI2'}, inplace=True)
			df_withlabels.drop(columns='index', inplace=True)


			output_current_file = connectome_dir + f"/{sub}_{ses}_SC_ROIs.csv" 
			df_withlabels.to_csv(output_current_file,mode = 'w', index=False)

			all_non_zero_entries.append(df_withlabels)


result_df = pd.concat(all_non_zero_entries)

# Write the result DataFrame to a new CSV file
output_file = result_dir + "/SC_ROIs_all_30m.csv" 
print(output_file) 
result_df.to_csv(output_file,mode = 'w', index=False)


		# print(result_dir)

# |Group | Sub-id | Ses-id | Metric | ROI1 | ROI2 |


