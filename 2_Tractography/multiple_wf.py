from nipype import SelectFiles, Node, Workflow, DataSink, IdentityInterface, MapNode
from nipype.interfaces.utility import Merge, Function
from bids.layout import BIDSLayout
import nipype.interfaces.mrtrix3 as mrt
from nipype.interfaces import fsl
from nipype.interfaces.fsl import ExtractROI
from nipype.interfaces.freesurfer import ReconAll
import cmtklib.interfaces.mrtrix3 as cmp_mrt
import os
import sys

from pipeline_parameters import *

from nipype import config, logging
config.enable_debug_mode()
logging.update_logging(config)

##########################################################
###########      Data Conversion       ###################
##########################################################

data_dir = sys.argv[1]
subject_raw = sys.argv[2]
session_raw = sys.argv[3]
base_directory = sys.argv[4]
out_dir = sys.argv[5]

print(data_dir)
print(base_directory)
print(out_dir)

tckgen_ntracks_param = int(sys.argv[6])

subject_list = subject_raw.split(',')
ses_list = session_raw.split(',')

############# DC : Node Definition #######################

infosource = Node(IdentityInterface(fields=['subject_id','ses_id']),
                  name="infosource")
infosource.iterables = [('subject_id', subject_list),('ses_id',ses_list)]

templates = {'anat': 'sub-{subject_id}/ses-{ses_id}/anat/sub-{subject_id}_ses-{ses_id}_T1w.nii.gz',
             'dwiPA': 'sub-{subject_id}/ses-{ses_id}/dwi/sub-{subject_id}_ses-{ses_id}_acq-*_dir-PA_dwi.nii.gz',
             'bvalPA': 'sub-{subject_id}/ses-{ses_id}/dwi/sub-{subject_id}_ses-{ses_id}_acq-*_dir-PA_dwi.bval',
             'bvecPA': 'sub-{subject_id}/ses-{ses_id}/dwi/sub-{subject_id}_ses-{ses_id}_acq-*_dir-PA_dwi.bvec',
             'dwiAP': 'sub-{subject_id}/ses-{ses_id}/dwi/sub-{subject_id}_ses-{ses_id}_acq-*_dir-AP_dwi.nii.gz',
             'bvalAP': 'sub-{subject_id}/ses-{ses_id}/dwi/sub-{subject_id}_ses-{ses_id}_acq-*_dir-AP_dwi.bval',
             'bvecAP': 'sub-{subject_id}/ses-{ses_id}/dwi/sub-{subject_id}_ses-{ses_id}_acq-*_dir-AP_dwi.bvec'
             }

sf = Node(SelectFiles(templates),
          name='sf')
sf.inputs.base_directory = data_dir

#### Conversion des DWI PA en .mif (utilisation du nifti, bvec et bval) + Concatenation
mrconvertPA = MapNode(mrt.MRConvert(),name = "mrconvertPA",iterfield = ['in_file','in_bvec','in_bval'])
mrcatPA = Node(mrt.MRCat(),name="mrcatPA")

### Conversion du DWI AP en .mif avec le nifti, bvec, bval
mrconvertAP = Node(mrt.MRConvert(),name = "mrconvertAP")

############# DC : Connecting the WF #######################

wf_dc = Workflow(name="wf_dc",base_dir = base_directory)
wf_dc.config['execution']['use_caching'] = 'True'
wf_dc.config['execution']['hash_method'] = 'content'


wf_dc.connect(infosource, "subject_id", sf, "subject_id")
wf_dc.connect(infosource, "ses_id", sf, "ses_id")

wf_dc.connect(sf,'dwiPA',mrconvertPA,'in_file')
wf_dc.connect(sf,'bvecPA',mrconvertPA, 'in_bvec')
wf_dc.connect(sf,'bvalPA',mrconvertPA, 'in_bval')

wf_dc.connect(sf,'dwiAP',mrconvertAP,'in_file')
wf_dc.connect(sf,'bvecAP',mrconvertAP, 'in_bvec')
wf_dc.connect(sf,'bvalAP',mrconvertAP, 'in_bval')

wf_dc.connect(mrconvertPA,'out_file',mrcatPA,'in_files')


############################################################
########          Freesurfer  Workflow           ###########
############################################################

os.environ["SUBJECTS_DIR"] = data_dir
fs_reconall = Node(ReconAll(),name = "fs_reconall")
fs_reconall.inputs.directive = reconall_param
#.inputs.subjects_dir = data_dir
fs_workflow = Workflow(name = 'fs_workflow',base_dir = base_directory)
fs_workflow.config['execution']['use_caching'] = 'True'
fs_workflow.config['execution']['hash_method'] = 'content'


fs_workflow.connect(infosource,'subject_id',fs_reconall,'subject_id')
fs_workflow.connect(sf,'anat',fs_reconall,'T1_files')


############################################################
########          Preprocessing Workflow           #########
############################################################

##########       Preproc: Node definition       ############

############# Denoising + Unring #############
denoise = Node(mrt.DWIDenoise(),name = 'denoise')
unring = Node(mrt.MRDeGibbs(),name = 'unring')

# extract b=0 channels from the DWI PA:
b0PA_extract = Node(mrt.DWIExtract(),name = 'b0PA_extract')
b0PA_extract.inputs.bzero = True
b0PA_extract.inputs.out_file ='b0PA.mif'

# Mean b=0 PA
avg_b0PA = Node(mrt.MRMath(),name = 'avg_b0PA')
avg_b0PA.inputs.operation = 'mean'
avg_b0PA.inputs.axis = 3
avg_b0PA.inputs.out_file = 'avg_b0PA.mif'

# extract b=0 channels from the DWI PA:

b0AP_extract = Node(mrt.DWIExtract(),name = 'b0AP_extract')
b0AP_extract.inputs.bzero = True
b0AP_extract.inputs.out_file ='b0AP.mif'

## Concat B=0 in reverse phase directions
merger_preproc = Node(Merge(2),name = 'merger')
mrcatb0 = Node(mrt.MRCat(),name = 'mrcatb0')
mrcatb0.inputs.axis = 3

### Topup -> Eddy ###

# # dwifslpreproc ${pref}_dwi_den_unr.mif ${pref}_dwi_den_unr_preproc.mif -pe_dir PA -rpe_pair -se_epi ${pref}_b0_pair.mif -eddy_options " --slm=linear "
#dwifslpreproc /mnt/CONHECT_data/pipeline_tmp/main_workflow/preproc/_ses_id_001_subject_id_01/unring/concatenated_denoised_unr.mif preproc.mif -rpe_pair -eddy_options "--slm=linear" -se_epi /mnt/CONHECT_data/pipeline_tmp/main_workflow/preproc/_ses_id_001_subject_id_01/mrcatb0/concatenated.mif -pe_dir j

dwpreproc = Node(mrt.DWIPreproc(),name = 'dwpreproc')
dwpreproc.inputs.rpe_options = 'pair'
dwpreproc.inputs.out_file = "preproc.mif"
#preproc.inputs.out_grad_mrtrix = "grad.b"    # export final gradient table in MRtrix format
dwpreproc.inputs.eddy_options = eddyoptions_param   # linear second level model and replace outliers
dwpreproc.inputs.pe_dir = 'PA'



# Unbias
biascorrect = Node(mrt.DWIBiasCorrect(),name = 'biascorrect')
biascorrect.inputs.use_ants = useants_param
biascorrect.inputs.out_file = 'biascorrect.mif'

##########           Preproc Connecting the WF         ##########

wf_preproc = Workflow(name = 'preproc',base_dir = base_directory)
wf_preproc.config['execution']['use_caching'] = 'True'
wf_preproc.config['execution']['hash_method'] = 'content'

wf_preproc.connect(denoise,'out_file',unring,'in_file')
wf_preproc.connect(unring,'out_file',b0PA_extract,'in_file')
wf_preproc.connect(b0PA_extract,'out_file',avg_b0PA,'in_file')
wf_preproc.connect(avg_b0PA,'out_file',merger_preproc,'in1')
wf_preproc.connect(b0AP_extract,'out_file',merger_preproc,'in2')
wf_preproc.connect(merger_preproc,'out',mrcatb0,'in_files')
wf_preproc.connect(unring,'out_file',dwpreproc,'in_file')
wf_preproc.connect(mrcatb0,'out_file',dwpreproc,'in_epi')
wf_preproc.connect(dwpreproc,'out_file',biascorrect,'in_file')


##################################################################
#########            Tractography             ####################
##################################################################


############    Tractography: Nodes definition       #############

# # Estimation du brain mask : FSL bet
# convert_mask2nii = Node(mrt.MRConvert(),name = "convert_mask2nii")
# convert_mask2nii.inputs.out_file = "dwi_preproc.nii"

# bet_mask = Node(fsl.BET(),name = 'bet_mask')
# bet_mask.inputs.mask = True
# # bet_mask.inputs.mask_file = 'mask.nii'

# convert_mask2mif = Node(mrt.MRConvert(),name = "convert_mask2mif")
# convert_mask2mif.inputs.out_file = 'mask_preproc.mif'

brainmask = Node(mrt.BrainMask(),name ='brainmask')
brainmask.out_file = 'brainmask.mif'

# DWI2response 
dwiresponse = Node(mrt.ResponseSD(),name = 'dwiresponse')
dwiresponse.inputs.algorithm = fod_algorithm_param
dwiresponse.inputs.csf_file = 'wm.txt'
dwiresponse.inputs.gm_file = 'gm.txt'
dwiresponse.inputs.csf_file = 'csf.txt'


#dwi2fod msmt_csd ${pref}_dwi_preproc.mif -mask ${pref}_mask_preproc.mif ${pref}_wm.txt ${pref}_wmfod.mif ${pref}_gm.txt ${pref}_gmfod.mif ${pref}_csf.txt ${pref}_csffod.mif
dwi2fod = Node(mrt.ConstrainedSphericalDeconvolution(),name = "dwi2fod")
dwi2fod.inputs.algorithm = csd_algorithm_param
dwi2fod.inputs.wm_txt = 'wm.txt' # ici faire le lien avec dwiresp
dwi2fod.inputs.wm_odf = 'wm.mif'
dwi2fod.inputs.csf_odf = "csf.mif"
dwi2fod.inputs.gm_odf = "gm.mif"

gen5tt = Node(mrt.Generate5tt(),name = 'gen5tt')
gen5tt.inputs.algorithm = tt_algorithm_param
gen5tt.inputs.out_file = '5tt.mif'

#dwiextract ${pref}_dwi_preproc.mif - -bzero | mrmath - mean ${pref}_mean_b0_preprocessed.mif -axis 3
b0_extract = Node(mrt.DWIExtract(),name = 'b0_extract')
b0_extract.inputs.bzero = True
b0_extract.inputs.out_file = 'b0_extract.mif'

avg_b0 = Node(mrt.MRMath(),name = 'avg_b0')
avg_b0.inputs.operation = 'mean'
avg_b0.inputs.axis = 3
avg_b0.inputs.out_file = 'avg_b0.mif'

convertb02nii = Node(mrt.MRConvert(),name = 'convertb02nii')
convertb02nii.inputs.out_file = 'b0.nii.gz'
convert5tt2nii = Node(mrt.MRConvert(),name = 'convert5tt2nii')
convert5tt2nii.inputs.out_file = '5tt.nii.gz'

#fslroi ${pref}_5tt_nocoreg.nii.gz ${pref}_5tt_vol0.nii.gz 0 1 #Extract the first volume of the 5tt dataset (since flirt can only use 3D images, not 4D images)
fslroi = Node(fsl.ExtractROI(roi_file='5tt_vol0.nii.gz', t_min=0,t_size=1),name = 'fslroi')

#flirt -in ${pref}_mean_b0_preprocessed.nii.gz -ref ${pref}_5tt_vol0.nii.gz -interp nearestneighbour -dof 6 -omat ${pref}_diff2struct_fsl.mat
flirt = Node(fsl.FLIRT(),name = 'flirt')
flirt.inputs.dof = flirt_dof_param
flirt.inputs.interp = flirt_interp_param
flirt.inputs.out_matrix_file = 'diff2struct_fsl.mat'

#transformconvert ${pref}_diff2struct_fsl.mat ${pref}_mean_b0_preprocessed.nii.gz ${pref}_5tt_nocoreg.nii.gz flirt_import ${pref}_diff2struct_mrtrix.txt
transformconvert = Node(mrt.TransformFSLConvert(),name = 'transformconvert')
transformconvert.inputs.flirt_import = True

# mrtransform ${pref}_5tt_nocoreg.mif -linear ${pref}_diff2struct_mrtrix.txt -inverse ${pref}_5tt_coreg.mif
# mrtransform ${pref}_T1_raw.mif -linear ${pref}_diff2struct_mrtrix.txt -inverse ${pref}_T1_coreg.mif
transform5tt = Node(mrt.MRTransform(),name = 'transform5tt')
#transform5tt.inputs.invert=True
transform5tt.inputs.out_file="5tt_coreg.mif"
transformT1 = Node(mrt.MRTransform(),name = 'transformT1')
#transformT1.inputs.invert=True
transformT1.inputs.out_file="T1_coreg.mif"

# gmwmi
gmwmi = Node(cmp_mrt.GenerateGMWMInterface(),name = 'gmwmi')
gmwmi.inputs.out_file = 'gmwmi.mif'

#tckgen -act ${pref}_5tt_coreg.mif -backtrack -seed_gmwmi ${pref}_gmwmSeed_coreg.mif -select 10000000 ${pref}_wmfod_norm.mif ${pref}_tracks_10mio.tck
tckgen = Node(mrt.Tractography(),name = 'tckgen')
tckgen.inputs.algorithm = tckgen_algorithm_param
tckgen.inputs.select = tckgen_ntracks_param
tckgen.inputs.backtrack = True

tcksift2 = Node(cmp_mrt.FilterTractogram(),name = 'tcksift2')
tcksift2.inputs.out_file = 'sift_tracks.tck'

#tcksift2.inputs.out_tracks = 'sift_tracks.tck'

#tcksift2.inputs.out_weights = 'finaltracks.tck'

#############     Tractography: Connecting the WF    ##################

wf_tractography = Workflow(name = "wf_tractography",base_dir = base_directory)
wf_tractography.config['execution']['use_caching'] = 'True'
wf_tractography.config['execution']['hash_method'] = 'content'

wf_tractography.connect(b0_extract,'out_file',avg_b0,'in_file')
wf_tractography.connect(avg_b0,'out_file',convertb02nii,'in_file')

wf_tractography.connect(gen5tt,'out_file',convert5tt2nii,'in_file')

wf_tractography.connect(convert5tt2nii,'out_file',fslroi,'in_file')
wf_tractography.connect(convertb02nii,'out_file',flirt,'in_file')
wf_tractography.connect(fslroi,'roi_file',flirt,'reference')

wf_tractography.connect(convertb02nii,'out_file',transformconvert,'in_file')
wf_tractography.connect(flirt,'out_matrix_file',transformconvert,'in_transform')
wf_tractography.connect(convert5tt2nii,'out_file',transformconvert,'reference')

wf_tractography.connect(gen5tt,'out_file',transform5tt,'in_files')

wf_tractography.connect(transformconvert,'out_transform',transform5tt,'linear_transform')
wf_tractography.connect(transformconvert,'out_transform',transformT1,'linear_transform')

wf_tractography.connect(transform5tt,'out_file',gmwmi,'in_file')

wf_tractography.connect(dwiresponse,'wm_file',dwi2fod,'wm_txt')
wf_tractography.connect(dwiresponse,'gm_file',dwi2fod,'gm_txt')
wf_tractography.connect(dwiresponse,'csf_file',dwi2fod,'csf_txt')
wf_tractography.connect(brainmask,'out_file',dwi2fod,'mask_file')


wf_tractography.connect(gmwmi,'out_file',tckgen,'seed_gmwmi')
wf_tractography.connect(transform5tt,'out_file',tckgen,'act_file')
wf_tractography.connect(dwi2fod,'wm_odf',tckgen,'in_file')

wf_tractography.connect(tckgen,'out_file',tcksift2,'in_tracks')
wf_tractography.connect(transform5tt,'out_file',tcksift2,'act_file')
wf_tractography.connect(dwi2fod,'wm_odf',tcksift2,'in_fod')

#######################################################################
############          Connectome construction          ################
#######################################################################

connectome = Workflow(name = 'connectome',base_dir = base_directory)
connectome.config['execution']['use_caching'] = 'True'
connectome.config['execution']['hash_method'] = 'content'

#labelconvert $datadir/anat/$sub_id/mri/aparc.a2009s+aseg.mgz $FREESURFER_HOME/FreeSurferColorLUT.txt ~/miniconda3/share/mrtrix3/labelconvert/fs_a2009s.txt $datadir/results/${sub_id}_${ses_id}_parcels_destrieux.mif -force

labelconvert = MapNode(mrt.LabelConvert(),name = 'labelconvert',iterfield=['in_file'])
labelconvert.inputs.in_config = labelconvert_param
labelconvert.inputs.in_lut = fs_lut_param

transform_parcels = MapNode(mrt.MRTransform(),name = 'transform_parcels',iterfield=['in_files'])
transform_parcels.inputs.out_file="parcels_coreg.mif"

#tck2connectome –symmetric –zero_diagonal tracks_10mio.tck ${sub_id}_${ses_id}_parcels_destrieux.mif ${sub_id}_${ses_id}_sc_connectivity_matrix.csv –out_assignment ${sub_id}_${ses_id}_sc_assignments.csv -force
tck2connectome = MapNode(mrt.BuildConnectome(),name = 'tck2connectome',iterfield=['in_parc'])
tck2connectome.inputs.zero_diagonal = True
tck2connectome.inputs.out_file = "connectome.csv"

#connectome.connect(tcksift2,'out_tracks',tck2connectome,'in_file')

connectome.connect(labelconvert,'out_file',transform_parcels,'in_files')
connectome.connect(transform_parcels,'out_file',tck2connectome,'in_parc')

######################################################################
######            Data Sink                           ################
######################################################################

def custom_output_path(out_dir,sub_id, ses_id):
    import os
    return os.path.join(out_dir, f"sub-{sub_id}/ses-{ses_id}")

datasink = Node(DataSink(), name="datasink")
datasink.inputs.parameterization = False
datasink.inputs.base_directory = out_dir  

custom_path = Node(Function(input_names=["out_dir","sub_id", "ses_id"],
                            output_names=["custom_path"],
                            function=custom_output_path),
                   name="custom_path")

#######################################################################
#########         Connecting Workflows together        ################
#######################################################################

main_wf = Workflow(name = "main_workflow",base_dir = base_directory)
main_wf.config['execution']['use_caching'] = 'True'
main_wf.config['execution']['hash_method'] = 'content'

# main_wf.connect(wf_dc,'infosource.subject_id',custom_path,'sub_id')
# main_wf.connect(wf_dc,'infosource.ses_id',custom_path,'ses_id')

main_wf.connect(wf_dc,'mrcatPA.out_file',wf_preproc,'denoise.in_file')
main_wf.connect(wf_dc,'mrconvertAP.out_file',wf_preproc,'b0AP_extract.in_file')
main_wf.connect(wf_preproc,'biascorrect.out_file',wf_tractography,'brainmask.in_file')
main_wf.connect(wf_preproc,'biascorrect.out_file',wf_tractography,'b0_extract.in_file')
main_wf.connect(wf_preproc,'biascorrect.out_file',wf_tractography,'dwiresponse.in_file')
main_wf.connect(wf_preproc,'biascorrect.out_file',wf_tractography,'dwi2fod.in_file')
main_wf.connect(wf_dc,'sf.anat',wf_tractography,'gen5tt.in_file')
main_wf.connect(wf_dc,'sf.anat',wf_tractography,'transformT1.in_files')
main_wf.connect(fs_workflow,'fs_reconall.aparc_aseg',connectome,'labelconvert.in_file')
main_wf.connect(wf_tractography,'transformconvert.out_transform',connectome,'transform_parcels.linear_transform')
main_wf.connect(wf_tractography,'tcksift2.out_tracks',connectome,'tck2connectome.in_file')
# main_wf.connect(custom_path, 'custom_path', datasink, 'base_directory')

# join_DC = Node(Merge(3), name='join_DC')
# main_wf.connect(wf_dc, 'mrcatPA.out_file', join_DC, 'in1')
# main_wf.connect(wf_dc, 'mrconvertAP.out_file', join_DC, 'in2')
# main_wf.connect(wf_dc,'sf.anat',join_DC,'in3')
# main_wf.connect(join_DC,'out',datasink,'1_DataConversion')

# main_wf.connect(wf_preproc,'biascorrect.out_file',datasink,'2_Preprocessing')

# join_FOD = Node(Merge(4), name='join_FOD')
# main_wf.connect(wf_tractography,'dwiresponse.wm_file',join_FOD,'in1')
# main_wf.connect(wf_tractography,'dwi2fod.wm_odf',join_FOD,'in2')
# main_wf.connect(wf_tractography,'transform5tt.out_file',join_FOD,'in3')
# main_wf.connect(wf_tractography,'transformT1.out_file',join_FOD,'in4')
# main_wf.connect(join_FOD,'out',datasink,'3_FODestimation')

# join_Tracto = Node(Merge(2), name='join_Tracto')
# main_wf.connect(wf_tractography,'tckgen.out_file',join_Tracto,'in1')
# main_wf.connect(wf_tractography,'tcksift2.out_tracks',join_Tracto,'in2')
# main_wf.connect(join_Tracto,'out',datasink,'4_Tractography')

# main_wf.connect(connectome,'tck2connectome.out_file',datasink,'5_Connectome')

main_wf.write_graph(graph2use='colored',dotfilename='./mult_11_12.dot')
wf_tractography.write_graph(graph2use='orig',dotfilename='./graph_tractography.dot')
wf_dc.write_graph(graph2use='orig',dotfilename='./graph_dc.dot')
connectome.write_graph(graph2use='orig',dotfilename='./graph_connectome.dot')

main_wf.run(plugin = 'MultiProc')
