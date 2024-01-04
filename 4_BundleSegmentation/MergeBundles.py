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
from copy import deepcopy
from matplotlib.colors import ListedColormap


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
	

def gen_sphere(x0,y0,z0,radius):

	size1,size2,size3 = 145,174,145 

	A = np.zeros((size1,size2, size3)) 

	AA = deepcopy(A) 

	
	for x in range(x0-radius, x0+radius+1):
	    for y in range(y0-radius, y0+radius+1):
	        for z in range(z0-radius, z0+radius+1):
	            ''' deb: measures how far a coordinate in A is far from the center. 
	                    deb>=0: inside the sphere.
	                    deb<0: outside the sphere.'''   
	            deb = radius - ((x0-x)**2 + (y0-y)**2 + (z0-z)**2)**0.5
	            if (deb)>=0: AA[x,y,z] = 1

	np.save('/mnt/CONHECT_data/code/4_BundleSegmentation/sphere_mask.npy',AA)

	nifti_img = nib.Nifti1Image(AA, affine=np.eye(4))

	# Save the NIfTI image to a file (replace 'output.nii.gz' with your desired filename)
	nib.save(nifti_img, '/mnt/CONHECT_data/code/4_BundleSegmentation/sphere_mask.nii.gz')

	return AA


def get_masked_infos(stack,sphere_mask,x0,y0,z0,radius):
    # stack = np.load(data_dir + '/stacked_mask.npy',allow_pickle=True).astype(np.int_)
    # sphere_mask = np.load('/mnt/CONHECT_data/code/test_sphere/sphere_mask.npy')

    print('Mask stacked data with the mask')
    masked_stack = np.zeros_like(stack)
    for k in range(stack.shape[3]):
        masked_stack[:,:,:,k] = np.multiply(stack[:,:,:,k],sphere_mask)
    print('done')


    size = np.shape(masked_stack)
    
    print('Truncate masked data to the smaller space')
    masked_trunc = masked_stack[x0-radius:y0+radius,y0-radius:y0+radius,z0-radius:z0+radius,:]
    print('done')

    return masked_trunc



def main_merge_bundles(bundle_dir,output_path,x0,y0,z0,radius):
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

	## Generate the sphere for masking
	sphere = gen_sphere(x0,y0,z0,radius)

	#### Plot intersection img + sphere | check sphere position
	# command = f'mrview {output_path} -voxel {x0},{y0},{z0} -overlay.load /mnt/CONHECT_data/code/4_BundleSegmentation/sphere_mask.nii.gz -mode 2'
	# subprocess.run(command, shell = True)


	#### Mask all_masks with sphere and plot the pie charts.

	masked_trunc = get_masked_infos(all_masks,sphere,x0,y0,z0,radius)

	L = []
	for k in range(masked_trunc.shape[3]):
	    L.append(np.sum(masked_trunc[:,:,:,k]))

	presentBundles = [x for x in L if x != 0]
	equi = pd.read_csv(f'{data_dir}/equivalence_bundle_table.csv')

	equi['in'] = L
	equi_chart = equi[equi['in']>0]


	### Plot bundle repartition as a pie chart

	labels = equi_chart['label']
	sizes = equi_chart['in']

	### Axe gauche droite : x, axe avant arriere : y, axe vertical z

	slice_ax = summed_mask[:,:,z0]
	slice_cor = summed_mask[:,y0,:]
	slice_sag = summed_mask[x0,:,:]
	sphere_ax = sphere[:,:,z0]
	sphere_cor = sphere[:,y0,:]
	sphere_sag = sphere[x0,:,:]

	fig, axs = plt.subplots(2, 2, figsize=(20, 10))

	# Plot the overlaid slice in the first subplot
	axs[0,0].imshow(np.rot90(slice_ax),cmap = 'gray')
	axs[0,0].imshow(np.rot90(sphere_ax),alpha = 0.9*(np.rot90(sphere_ax)>0),cmap = 'hot')
	axs[0,0].set_title('Overlay of axial Slice')
	axs[0,0].invert_xaxis()
	axs[0,0].set_axis_off()

	axs[0,1].pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
	axs[0,1].set_title('Bundle composition inside the sphere')

	axs[1,0].imshow(np.rot90(slice_cor),cmap = 'gray')
	axs[1,0].imshow(np.rot90(sphere_cor),alpha = 0.9*(np.rot90(sphere_cor)>0),cmap = 'hot')
	axs[1,0].set_title('Overlay of coronal Slice')
	axs[1,0].invert_xaxis()
	axs[1,0].set_axis_off()
	
	axs[1,1].imshow(np.rot90(slice_sag),cmap = 'gray')
	axs[1,1].imshow(np.rot90(sphere_sag),alpha = 0.9*(np.rot90(sphere_sag)>0),cmap = 'hot')
	axs[1,1].set_title('Overlay of sagittal Slice')
	axs[1,1].invert_xaxis()
	axs[1,1].set_axis_off()


	plt.tight_layout()
	plt.show()

	#### Plot intersection img + sphere | check sphere position
	command = f'mrview {output_path} -voxel {x0},{y0},{z0} -overlay.load /mnt/CONHECT_data/code/4_BundleSegmentation/sphere_mask.nii.gz -mode 2'
	subprocess.run(command, shell = True)



bundle_dir = data_dir + '/tractseg_output/bundle_segmentations'
output_path = f"{data_dir}/intersection_test.nii.gz"



main_merge_bundles(bundle_dir,output_path,84,127,48,5)
