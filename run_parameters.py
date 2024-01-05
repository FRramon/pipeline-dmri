################################################################
######                    Instructions                   #######
################################################################


convert2bids = False
run_pipeline = True

createMatrixes = False
createROIfile = False
QAcheck = False
bundleSegmentation= False
ClusterConsensus = False


#### 				     	INPUTS        	                ####


source_dir = '/mnt/CONHECT_data'
data_folder = 'nifti3'
group = 'Patients'
session_list = ['003']

pipe_name = 'pipe_patients_30'
result_name = 'results_patients_30'
ntracks = 30000000

