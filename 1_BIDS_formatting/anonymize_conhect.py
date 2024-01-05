import os
import shutil
import csv
import pandas as pd
import re


#################################################################
# This script rename subjects by sub...  #
# And sessions by ses-...                                       #
# Leaves an equivalence table for unique identifiers            #
#################################################################


def anonymize_conhect(base_dir):
	print('running anonymize_conhect')
	# Examine content of the folder and select with a regular expression the right format file
	os.chdir(base_dir)
	groups = os.listdir(base_dir)
	groups = ['Patients']

	n=0

	for g in groups:

		rawdata_path = os.path.join(base_dir,g)
		inrawdata = os.listdir(rawdata_path)
		print(inrawdata)
		# Check patients label are the right
		pattern = re.compile(r'\d-\D{1}-\d{3}-[A-Za-z]{2}')
		subjects = [s for s in inrawdata if pattern.match(s)]

		subjects_new = []
		subjects_old = []

		os.chdir(rawdata_path)

		print("Rename subjects by sub-01 ...")
		nsub=0
		for i , s in enumerate(subjects):	
			print(s)
			if n+i<=8:
				subname = "sub-0" + str(n+i+1)
			if n+i>8:
				subname = "sub-" + str(n+i+1)
			print(subname)
			os.rename(s,subname)
			subjects_new.append(subname)
			subjects_old.append(s)
			nsub+=1

		n+=nsub

		print(subjects_new)	
		print("Rename the session by ses-001 ...")

		for sub in subjects_new:
			subdir = os.path.join(rawdata_path,sub)
			sessions = os.listdir(subdir)
			os.chdir(subdir)
			if 'V1' in sessions:
				os.rename('V1','ses-001')
			if 'V2' in sessions:
				os.rename('V2','ses-002')
			if 'V3' in sessions:
				os.rename('V3','ses-003')

		#create a .csv equivalence table into the main folder (rawdata)
		if not os.path.isfile(os.path.join(rawdata_path, f"equivalence_table_{g}.csv")):
			equivalence_table = pd.DataFrame(list(zip(subjects_old, subjects_new)), columns =['conhect_label', 'sub_number'])
			equivalence_table.to_csv(os.path.join(rawdata_path, f"equivalence_table_{g}.csv"), index=False)

		print("Finish")


#anonymize_conhect('/mnt/CONHECT_data/data')

def correct_names(base_dir):
	print('running name correction')
	# Examine content of the folder and select with a regular expression the right format file
	os.chdir(base_dir)
	groups = os.listdir(base_dir)
	groups = ['Patients']

	n=0

	for g in groups:

		rawdata_path = os.path.join(base_dir,g)
		inrawdata = os.listdir(rawdata_path)
		#print(inrawdata)
		# Check patients label are the right
		pattern = re.compile(r'^sub-\d')
		subjects = [s for s in inrawdata if pattern.match(s)]

		subjects_new = []
		subjects_old = []

		os.chdir(rawdata_path)

		print("Rename subjects by sub-01 ...")
		nsub=0
		for i , s in enumerate(subjects):	
		
			print(s[4:])
			if len(s[4:]) == 3:
				subname = 'sub-' + s[5:]
				print(f'new name : {subname}')
				os.rename(s,subname)

  
