
import networkx as nx
import numpy as np
import os
import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import scipy
import random

source_dir = '/mnt/CONHECT_data'


df = pd.read_csv('/home/francoisramon/test2.csv')

def get_cluster_number(df):
	return df['cluster'].nunique()

def generate_random_rgb():
    return f'{random.randint(0, 255)}'

n=get_cluster_number(df)
print(n)
clusters = ['C'+str(i) for i in range(1,n+1)]


random_R = [generate_random_rgb() for _ in range(n)]
random_G = [generate_random_rgb() for _ in range(n)]
random_B = [generate_random_rgb() for _ in range(n)]
r255 = ['255' for _ in range(n)]

# # Create DataFrame with 'cluster' and 'colour' columns
color_df = pd.DataFrame({'cluster': clusters[:n], 'R': random_R,'G': random_G,'B': random_B,'A': r255})


clustercolor_df = pd.merge(df['cluster'],color_df, on='cluster')
indexes = [i+1 for i in range(clustercolor_df.shape[0])]
clustercolor_df['index'] = indexes

print(f"Number of rows in the resulting DataFrame: {clustercolor_df.shape[0]}")



input_lut = source_dir + '/code/fs_a2009s.txt'
df_labelconvert = pd.read_csv(input_lut,delim_whitespace = True, comment = '#',header=None, names=['index', 'labelname', 'R', 'G', 'B', 'A'])

print(f"Number of rows in the labelconvert DataFrame: {df_labelconvert.shape[0]}")


full_df = pd.merge(clustercolor_df,df_labelconvert[['index','labelname']],on='index')


df_LUT = full_df[['index','labelname','R','G','B','A']]
print(df_LUT.head())

output_file_path = '/home/francoisramon/sub-01_ses-001_customLUT.txt'
df_LUT.to_csv(output_file_path, sep='	', index=False,header=None)

