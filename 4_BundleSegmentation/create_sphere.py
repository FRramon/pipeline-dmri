import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import nibabel as nib
data_dir = '/mnt/CONHECT_data/pipe_upto_21dec/main_workflow/bundle_segmentation/_ses_id_001_subject_id_02'
import pyrr

# def create_sphere(nx, ny, nz, center, radius):
#     sphere_array = np.zeros((nx, ny, nz))
#     for x in range(nx):
#         for y in range(ny):
#             for z in range(nz):
#                 distance_to_center = np.linalg.norm(np.array([x, y, z]) - np.array(center))
#                 if distance_to_center <= radius:
#                     sphere_array[x, y, z] = 1
#     return sphere_array


import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def create_sphere(nx, ny, nz, center, radius):
    r = radius
    pi = np.pi
    cos = np.cos
    sin = np.sin
    phi, theta = np.mgrid[0.0:pi:100j, 0.0:2.0*pi:100j]
    x = r * sin(phi) * cos(theta)
    y = r * sin(phi) * sin(theta)
    z = r * cos(phi)

    # Scale the sphere to fit inside the given dimensions
    x_scaled = (x + 1) * (nx - 1) / 2
    y_scaled = (y + 1) * (ny - 1) / 2
    z_scaled = (z + 1) * (nz - 1) / 2

    # Translate the sphere to the specified center position
    x_scaled += center[0]
    y_scaled += center[1]
    z_scaled += center[2]

    # Round the scaled coordinates to integers
    x_rounded = np.round(x_scaled).astype(int)
    y_rounded = np.round(y_scaled).astype(int)
    z_rounded = np.round(z_scaled).astype(int)

    # Create the sphere array
    sphere_array = np.zeros((nx, ny, nz))
    sphere_array[x_rounded, y_rounded, z_rounded] = 1

    return sphere_array

# Example parameters
nx, ny, nz = 100, 100, 100
radius = 4
center = [30, 30, 30]

# Create the sphere
sphere_array = create_sphere(nx, ny, nz, center, radius)


# Plotting with adjusted figure size
fig = plt.figure(figsize=(nx, ny))
ax = fig.add_subplot(111, projection='3d')

# Extracting coordinates of points where the array is 1
x, y, z = np.where(sphere_array == 1)

ax.scatter(x, y, z, c='r', marker='o', label='Inside Sphere')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Sphere')

plt.show()


# nx, ny, nz = 20, 20, 20
# cx,cy,cz = [5, 5, 5]
# r = 4

# # Create the sphere
# sphere_array = create_sphere(cx, cy, cz, r)


# sphere_array = sphere_array.astype(np.float32)
    
# sphere_img = nib.Nifti1Image(sphere_array, affine=np.eye(4))
# sphere_img.set_data_dtype(np.float32)

# nib.save(sphere_img, f'{data_dir}/sphere.nii.gz')


# # # Plotting
# # fig = plt.figure(figsize=(nx, ny))
# # ax = fig.add_subplot(111, projection='3d')

# # # Extracting coordinates of points where the array is 1
# # x, y, z = np.where(sphere_array == 1)

# # ax.scatter(x, y, z, c='r', marker='o', label='Inside Sphere')
# # ax.set_xlabel('X')
# # ax.set_ylabel('Y')
# # ax.set_zlabel('Z')
# # ax.set_title('3D Sphere')

# # plt.show()
