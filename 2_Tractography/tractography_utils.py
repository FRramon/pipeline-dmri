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
  
        # Checking if the directory is empty or not 
        if not os.listdir(path): 
            return True
        else: 
            return False 
    else: 
        return True


def get_list_sessions(base_dir,groups,session):

	# Get subjects ids which participated in session i

	source_data_dir = os.path.join(base_dir,'data',groups)

	subjects_raw = os.listdir(source_data_dir)
	pattern = re.compile(r'^sub-\d')
	subjects = [s for s in subjects_raw if pattern.match(s)]

	haveSes = []

	for s in subjects:
		ses_id = 'ses-' + session
		ses_path = os.path.join(source_data_dir,s,ses_id)
		if not isEmpty(ses_path):
			haveSes.append(s)
	print(haveSes)
	print(len(haveSes))

	return haveSes


get_list_sessions('/mnt/CONHECT_data','Patients','003')