#MergeBundles**
import os
import subprocess
from sympy import primerange,factorint
import dipy
from dipy.io.image import load_nifti, save_nifti
import matplotlib.pyplot as plt
import numpy as np
import nibabel as nib
import pandas as pd

data_dir = '/mnt/CONHECT_data/pipe_upto_21dec/main_workflow/bundle_segmentation/_ses_id_001_subject_id_02'


# #print(os.listdir(data_dir))
# bundlemif_dir = data_dir + '/tractseg_output/bundles_mif'
# if not os.path.exists(bundlemif_dir):
# 	os.mkdir(bundlemif_dir)
	


#from pathlib import Path

def create_intersection_image(bundle_dir, mask_paths, output_path):
    # Load all the masks into a NumPy array
    print(mask_paths[1])
    masks = [load_nifti(f'{bundle_dir}/{path}')[0] for path in mask_paths]
    masks = np.stack(masks, axis=-1)
    np.save(f'{bundle_dir}/stacked_mask.npy',masks)
    return masks


def create_equivalence_table(bundle_dir):
	n = len(os.listdir(bundle_dir))
	indexes = [i for i in range(n)]
	labels = [X[:-7] for X in os.listdir(bundle_dir)]
	equi = pd.DataFrame({'index' : indexes, 'label' : labels})

	print(equi.head())
	equi.to_csv(f'{data_dir}/equivalence_bundle_table.csv')

	return equi
	

# Example usage:

#create_intersection_image(bundle_dir,mask_paths, output_path)



def main_merge_bundles(bundle_dir,output_path):
	mask_paths = os.listdir(bundle_dir)

	print('Concatenate bundle masks')
	#all_masks = create_intersection_image(bundle_dir, mask_paths, output_path)
	all_masks = np.load(f'{data_dir}/stacked_mask.npy')

	print('Get intersection heatmap and save to nii')
	summed_mask = np.sum(all_masks,axis = 3)

	# Save to nifti
	summed_mask = summed_mask.astype(np.float32)
	
	intersection_img = nib.Nifti1Image(summed_mask, affine=np.eye(4))
	intersection_img.set_data_dtype(np.float32)

    # Save the Nifti image
	nib.save(intersection_img, output_path)

	print('Construct the belonging bundles intersections')

	equi = create_equivalence_table(bundle_dir)

	LabelledImage = np.zeros((all_masks.shape[0],all_masks.shape[1],all_masks.shape[2],1),dtype = object)

	for i in range(all_masks.shape[0]):
		for j in range(all_masks.shape[1]):
			for k in range(all_masks.shape[2]):
				overlapping = np.where(all_masks[i,j,k,:] !=0 )
				print(overlapping)
				LabelledImage[i,j,k,0] = [equi['label'][z] for z in overlapping]

	np.save(f'{bundle_dir}/LabelledImage.npy',LabelledImage)




bundle_dir = data_dir + '/tractseg_output/bundle_segmentations'
output_path = f"{data_dir}/intersection_test.nii.gz"
#create_equivalence_table(bundle_dir)
main_merge_bundles(bundle_dir,output_path)
