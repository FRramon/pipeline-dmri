from __future__ import annotations

from typing import Optional

from heudiconv.utils import SeqInfo


def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template, outtype, annotation_classes


def infotodict(seqinfo):
    """Heuristic evaluator for determining which runs belong where

    allowed template fields - follow python string module:

    item: index within category
    subject: participant id
    seqitem: run number during scanning
    subindex: sub index within group
    """

    data = create_key("run{item:03d}")
    
    t1w = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_T1w')
    flair = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_FLAIR')

    dwi_6dirs_b2500 = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_acq-6dirs_dir-AP_dwi')
    dwi_30dirs_b200 = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_acq-30dirs_dir-PA_dwi')
    dwi_45dirs_b1500 = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_acq-45dirs_dir-PA_dwi')
    dwi_60dirs_b2500 = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_acq-60dirs_dir-PA_dwi')

    rsfmri = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-rest_bold')
    asl = create_key('sub-{subject}/{session}/perf/sub-{subject}_{session}_asl')
    
    info = {t1w: [], flair: [],dwi_6dirs_b2500: [],dwi_30dirs_b200: [], dwi_45dirs_b1500: [], dwi_60dirs_b2500: [], rsfmri: [], asl: []}
    last_run = len(seqinfo)

    for idx,s in enumerate(seqinfo):
       if ('3DT1' in s.series_description):
          info[t1w].append(s.series_id)
       if ('T2 FLAIR premiere aq' in s.series_description):
          info[flair].append(s.series_id)
       if ('PEP1 DTI 6dir b2500 HB2' in s.series_description):
          info[dwi_6dirs_b2500].append(s.series_id)
       if ('PEP0 DTI 60dir b2500 HB2' in s.series_description):
          info[dwi_60dirs_b2500].append(s.series_id)
       if ('PEP0 DTI 45dir b1500 HB2' in s.series_description):
          info[dwi_45dirs_b1500].append(s.series_id)
       if ('PEP0 DTI 30dir b200 HB2' in s.series_description):
          info[dwi_30dirs_b200].append(s.series_id)
       if ('RsFMRI' in s.series_description):
          info[rsfmri].append(s.series_id)
       if ('3D ASL (non-contrast)' in s.series_description):
          info[asl].append(s.series_id)  
    return info
