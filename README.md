# Connectomics Pipeline

Features a versatile pipeline for BIDS data conversion, tractography, connectome matrix creation, and bundle segmentation.

**Author**: François Ramon | francois.ramon@ghu-paris.fr

## Usage

**Dependencies** : Python, Mrtrix3, FSL, FreeSurfer, ANTs

**Python packages** : nipype, nibabel, dcm2niix, heudiconv...

Adjust boolean flags in `pipeline_instructions.py` to control pipeline stages:

### I. BIDS Formatting & Correct AP/PA

run a BIDS formatting step using heudiconv & dcm2niix if :

``` python
convert2bids = True
```

### II. Tractography/Freesurfer Pipeline

This tractography pipeline is designed as the BATMAN mrtrix3 tutorial

Execute the following pipeline with 
``` python
run_pipeline = True
```
Adjust subject/session lists.
![image](https://github.com/FRramon/pipeline-dmri/assets/109392345/e5c0e987-3cad-48a9-a409-8407711217e8)


### III. Create Connectivity Matrices

Create Streamline Count (SC) and Fractional Anisotropy (FA) weighted connectivity matrixes

To generate matrices, set :
``` python
createMatrixes = True
```

### IV. Bundle Segmentation

Execute the following bundle identification using TractSeg
``` python
bundleSegmentation = True
```

![image](https://github.com/FRramon/pipeline-dmri/assets/109392345/6816fd8d-8569-46c3-ad7a-603eaad1a35e)

### QA Check

Enable QA check by setting : 
``` python
QAcheck = True
```
