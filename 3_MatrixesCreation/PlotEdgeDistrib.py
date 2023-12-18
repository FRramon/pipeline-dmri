import subprocess
import os
import sys
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

sc_file_path = "/mnt/CONHECT_data/pipe_healthy/main_workflow/connectome/_ses_id_001_subject_id_02/sc/sc_connectivity_matrix.csv"
fa_file_path = "/mnt/CONHECT_data/pipe_healthy/main_workflow/connectome/_ses_id_001_subject_id_02/fa/fa_connectivity_matrix.csv"

# df_sc = pd.read_csv(sc_file_path, header=None)
# outlier = df_sc.stack().quantile(0.999)
# plt.figure(figsize=(10, 8))
# sns.heatmap(df_sc, cmap='viridis', vmin=0,vmax = outlier, annot = False, fmt=".2f")
# #plt.title(f' sub-{sub} - ses-{ses} - {label}')

sc_adjacency_matrix = np.genfromtxt(sc_file_path, delimiter=',')

# Extract upper triangular part of the symmetric matrix (excluding diagonal)
sc_upper_triangle = np.triu(sc_adjacency_matrix, k=1)

# Flatten the upper triangular matrix to get the edge weights
sc_edge_weights = sc_upper_triangle.flatten()
non_zero_sc_edge_weights = sc_edge_weights[sc_edge_weights > 0]

fa_adjacency_matrix = np.genfromtxt(fa_file_path, delimiter=',')

# Extract upper triangular part of the symmetric matrix (excluding diagonal)
fa_upper_triangle = np.triu(fa_adjacency_matrix, k=1)

# Flatten the upper triangular matrix to get the edge weights
fa_edge_weights = fa_upper_triangle.flatten()
non_zero_fa_edge_weights = fa_edge_weights[fa_edge_weights > 0]

# Plot both distributions side by side using subplots
fig, axs = plt.subplots(2, 2, figsize=(20,10))

# Plot the distribution of sc edge weights
axs[0,0].hist(non_zero_sc_edge_weights, bins=40, edgecolor='black')
axs[0,0].set_title('Distribution of SC Edge Weights')
axs[0,0].set_xlabel('SC Edge Weight')
axs[0,0].set_ylabel('Frequency')

# Plot the log distribution of sc edge weights
axs[0,1].hist(non_zero_sc_edge_weights, bins=40, edgecolor='black')
axs[0,1].set_title('Log Distribution of SC Edge Weights')
axs[0,1].set_xlabel('Log(SC Edge Weight)')
axs[0,1].set_ylabel('Frequency')
axs[0,1].set_yscale('log')


# Plot the distribution of fa edge weights
axs[1,0].hist(non_zero_fa_edge_weights, bins=40, edgecolor='black')
axs[1,0].set_title('Distribution of FA Edge Weights')
axs[1,0].set_xlabel('FA Edge Weight')
axs[1,0].set_ylabel('Frequency')

# # Plot the log distribution of fa edge weights
# axs[1,1].hist(non_zero_fa_edge_weights, bins=40, edgecolor='black')
# axs[1,1].set_title('Log Distribution of FA Edge Weights')
# axs[1,1].set_xlabel('Log(FA Edge Weight)')
# axs[1,1].set_ylabel('Frequency')
# axs[1,1].set_yscale('log')

output_file_path_sc = "/mnt/CONHECT_data/pipe_healthy/main_workflow/connectome/_ses_id_001_subject_id_02/sc/distribution_edge_weights.png"
output_file_path_fa = "/mnt/CONHECT_data/pipe_healthy/main_workflow/connectome/_ses_id_001_subject_id_02/fa/distribution_edge_weights.png"

plt.savefig(output_file_path_fa)
plt.savefig(output_file_path_sc)

plt.show()
