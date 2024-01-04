###########################################################################
###           		 Provide utils functions                            ###
###########################################################################




import os
import shutil
import csv
import pandas as pd
import re



# Function to Check if the path specified 
# specified is a valid directory 
def isEmpty(path): 
    if os.path.exists(path) and not os.path.isfile(path): 
        #print(os.listdir(path))
        # Checking if the directory is empty or not 
        if not os.listdir(path): 
            return True
        else: 
            return False 
    else: 
        return True


def get_list_sessions(base_dir,groups,session):

	# Get subjects ids which participated in session i

	source_data_dir = os.path.join(base_dir,'nifti3',groups)

	subjects_raw = os.listdir(source_data_dir)
	pattern = re.compile(r'^sub-\d')
	subjects = [s for s in subjects_raw if pattern.match(s)]

	haveSes = []

	for s in subjects:
		#print(s)
		ses_id = 'ses-' + session
		ses_path = os.path.join(source_data_dir,s,ses_id)
		#print(ses_path)
		#print(isEmpty(ses_path))
		if not isEmpty(ses_path):
			haveSes.append(s)

	haveSes = [s[4:] for s in haveSes]

	print(len(haveSes))

	transformed_list = ','.join(haveSes)
	result_list = [transformed_list]

	print(result_list)

	return result_list


#get_list_sessions('/mnt/CONHECT_data','Patients','003')