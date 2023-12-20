
import os
import pandas as pd

input_file = '/mnt/CONHECT_data/code/fs_a2009s.txt'
input_cortical = '/mnt/CONHECT_data/results_test2/sub-01/ses-001/5_Connectome/sub-01_ses-001_SC_ROIs.csv'

df = pd.read_csv(input_file,delim_whitespace = True, comment = '#',header=None, names=['index', 'labelname', 'R', 'G', 'B', 'A'])
# head = |index|labelname|
print(df.head())

df_cortical = pd.read_csv(input_cortical)
# head = |subject|session|i|j|fibernumber|
print(df_cortical.head())

# #### I would like the output head = |subject|session|i|j|fibernumber|ROI1|ROI2|
# where ROI1 = the labelname corresponding to index i in df


# Merge the DataFrames based on 'i' for ROI1
result_df = pd.merge(df_cortical, df[['index', 'labelname']], left_on='i', right_on='index', how='left')
result_df.rename(columns={'labelname': 'ROI1'}, inplace=True)
result_df.drop(columns='index', inplace=True)

# Merge again for 'j' to get ROI2
result_df = pd.merge(result_df, df[['index', 'labelname']], left_on='j', right_on='index', how='left')
result_df.rename(columns={'labelname': 'ROI2'}, inplace=True)
result_df.drop(columns='index', inplace=True)

# Display the resulting DataFrame
print(result_df.head())

output_file = "/mnt/CONHECT_data/results_test2/sub-01/ses-001/5_Connectome/SC_ROIs.csv" 
print(output_file) 
result_df.to_csv(output_file,mode = 'w', index=False)
