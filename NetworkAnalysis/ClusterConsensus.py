########### Importing necessary libraries ###########

import networkx as nx
import numpy as np
import os
import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import scipy
import sknetwork as skn
from sklearn.cluster import SpectralClustering
import random
from collections import defaultdict



sub = sys.argv[1]
ses = sys.argv[2]
source_dir = sys.argv[3]

from ClusterConsensusParameters import *


###########          Louvain Clustering                                    ###########
def louvain_clustering(mat, r):
    model = skn.clustering.Louvain(resolution=r, verbose=False).fit(mat)
    labels = model.labels_
    return labels


def invert_non_zero_elements(matrix):
    # Find the non-zero elements
    non_zero_indices = matrix != 0
    
    # Invert the non-zero elements
    inverted_elements = 1 / matrix[non_zero_indices]
    
    # Assign the inverted elements back to the original matrix
    matrix[non_zero_indices] = inverted_elements
    
    return matrix


def co_classification_matrix(adjacency_matrix, gamma_min, gamma_max, num_clusterings):
    
    co_class_matrix = np.zeros((adjacency_matrix.shape[0], adjacency_matrix.shape[1]))

    for k in range(1, num_clusterings):
        gamma = gamma_min + (gamma_max - gamma_min) * (k / num_clusterings)
        print(f'running on k = {k} | gamma = {gamma}')
        labels_k = louvain_clustering(adjacency_matrix, gamma)

        for i in range(adjacency_matrix.shape[0]):
            for j in range(adjacency_matrix.shape[1]):
                if labels_k[i] == labels_k[j]:
                    co_class_matrix[i, j] += 1

    return co_class_matrix / num_clusterings


def get_cluster_classes(den, label='ivl'):
    cluster_idxs = defaultdict(list)
    for c, pi in zip(den['color_list'], den['icoord']):
        for leg in pi[1:3]:
            i = (leg - 5.0) / 10.0
            if abs(i - int(i)) < 1e-5:
                cluster_idxs[c].append(int(i))

    cluster_classes = {}
    for c, l in cluster_idxs.items():
        i_l = [den[label][i] for i in l]
        cluster_classes[c] = i_l

    return cluster_classes


def get_co_classification_matrix(adjacency_matrix,gamma_min,gamma_max,num_clusterings):

 
    co_class_matrix = co_classification_matrix(adjacency_matrix,gamma_min,gamma_max,num_clusterings)

    ########### Creating a DataFrame from the co-classification matrix ###########
    df_coclass = pd.DataFrame(co_class_matrix)
    plt.title("Co classification matrix")
    outlier = df_coclass.stack().quantile(0.99)

    ########### Plotting the clustered heatmap ###########
    ClustMap = sns.clustermap(df_coclass, cmap=sns.color_palette("coolwarm", n_colors=100))
    #plt.show()
    ########### Dendrogram for cluster visualization ###########
    den = scipy.cluster.hierarchy.dendrogram(ClustMap.dendrogram_col.linkage,
                                             labels=df_coclass.index,
                                             color_threshold=0.60)
    

    ########### Extracting clusters from dendrogram ###########
    clusters = get_cluster_classes(den)

    ########### Assigning cluster labels to each row in the co-classification matrix ###########
    cluster = []
    for i in df_coclass.index:
        print(i)
        included = False
        for j in clusters.keys():
            if i in clusters[j]:
                cluster.append(j)
                included = True
        if not included:
            cluster.append(None)


    # print(len(clusters['C1']))
    # print(len(clusters['C0']))
    # print(len(clusters['C2']))
 
    print(df_coclass.shape[0])
    print(cluster)

    print(len(cluster))
    df_coclass["cluster"] = cluster
    # ########### Saving the co-classification matrix to a CSV file ###########

    df_coclass.to_csv('/home/francoisramon/test2.csv')

    return ClustMap,den,df_coclass


def get_cluster_number(df):
        return df['cluster'].nunique()


def generate_random_rgb():
    return f'{random.randint(0, 255)}'



def createCustomLUT(source_dir,df_coclass):

  

    n = get_cluster_number(df_coclass)
    print(n)
    clusters = ['C' + str(i) for i in range(1, n + 1)]

    random_R = [generate_random_rgb() for _ in range(n)]
    random_G = [generate_random_rgb() for _ in range(n)]
    random_B = [generate_random_rgb() for _ in range(n)]
    r255 = ['255' for _ in range(n)]

    ############## Create DataFrame with 'cluster' and 'colour' columns ##############
    color_df = pd.DataFrame({'cluster': clusters[:n], 'R': random_R, 'G': random_G, 'B': random_B, 'A': r255})
    print(color_df)
    ############## Merging cluster DataFrame with color DataFrame ##############
    clustercolor_df = pd.merge(df_coclass['cluster'], color_df, on='cluster')
    indexes = [i+1 for i in range(clustercolor_df.shape[0])]
    clustercolor_df['index'] = indexes

    ############## Reading fs2009a LUT text file ##############
    input_lut = source_dir + '/code/fs_a2009s.txt'
    df_labelconvert = pd.read_csv(input_lut, delim_whitespace=True, comment='#', header=None,
                                  names=['index', 'labelname', 'R', 'G', 'B', 'A'])

    ############## Merging DataFrames to create a full DataFrame ##############
    full_df = pd.merge(clustercolor_df, df_labelconvert[['index', 'labelname']], on='index')

    ############## Creating final dataframe ##############
    df_LUT = full_df[['index', 'labelname', 'R', 'G', 'B', 'A']]
    print(df_LUT.head())



    return df_LUT



def main(source_dir,sub,ses,gamma_min,gamma_max,num_clusterings):

    input_file = source_dir + f'/pipe_healthy/main_workflow/connectome/_ses_id_{ses}_subject_id_{sub}/tck2connectome/mapflow/_tck2connectome2/connectome.csv'

    ########### Reading the connectivity matrix from the CSV file ###########
    df = pd.read_csv(input_file, header=None)
    Mat = df.to_numpy()

    ########### Ensuring symmetry in the connectivity matrix ###########
    Mat = Mat + Mat.T
    if inverse:
        Mat = invert_non_zero_elements(Mat)

    ClustMap,den,df_coclass = get_co_classification_matrix(Mat,gamma_min,gamma_max,num_clusterings)

    if viewMat:
        plt.figure()
        plt.show()


    df_LUT = createCustomLUT(source_dir,df_coclass)

    output_file_path = source_dir + f'/results_test2/sub-{sub}/ses-{ses}/5_Connectome/sub-{sub}_ses-{ses}_customLUT.txt'
    df_LUT.to_csv(output_file_path, sep=' ', index=False,header=None)
    


if __name__ == '__main__':
    main(source_dir,sub,ses,gamma_min,gamma_max,num_clusterings)