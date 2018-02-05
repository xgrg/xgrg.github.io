Title: Collecting image statistics from Regions-of-Interest over many subjects
Category: Python
Status: Published
Tags: python, image
Authors: Grégory Operto

Collecting basic image statistics (_e.g._ mean, std) from ROIs over a set of images can be done easily in Python.

<!-- PELICAN_END_SUMMARY -->


The function `regions_values` will take at least the

   :::python
   import numpy as np
   import nibabel as nib
   import logging as log
   from glob import glob
   import pandas as pd
   from joblib import Parallel, delayed
   import argparse

   def __region_values__(map_fp, atlas, func):
       m = np.array(nib.load(map_fp).dataobj)
       n_labels = len(np.unique(atlas))
       label_values = [func(m[atlas==label]) for label in range(1, n_labels)]
       return label_values

   def regions_values(atlas_fp, maps_fp, subjects=None, labels=None, func=np.mean,
           n_jobs=7):

       atlas_res = nib.load(atlas_fp).header['pixdim'][:4]
       log.info('Atlas resolution: %s'%str(atlas_res))
       atlas = np.array(nib.load(atlas_fp).dataobj)

       n_labels = len(np.unique(atlas))
       log.info('%s labels in %s'%(n_labels, atlas_fp))


       df = Parallel(n_jobs=n_jobs, verbose=1)(\
           delayed(__region_values__)(maps_fp[i], atlas, func)\
           for i in xrange(len(maps_fp)))

       columns = labels if not labels is None \
               else [str(e) for e in range(1, n_labels)]

       res = pd.DataFrame(df, columns=columns)

       res['subject'] = xrange(len(maps_fp)) if subjects is None else subjects
       res = res.set_index('subject')

       return res


This will be the result.

Test:
----------

   :::python
   atlas_fp = '/home/grg/SPM/2016-2017/ROIapoE/ROI_DARTEL/csf5/rois.nii.gz'
   maps_fp = glob('/home/grg/data/ALFA_DWI/dartel_ALFA_DWI/dartel_csf.5/rswr*.nii')
   subjects = [e.split('/')[-1][4:9] for e in maps_fp]
   names = {1: 'Middle cerebellar peduncle', 2: 'Pontine crossing tract (a part of MCP)',  3: 'Genu of corpus callosum',
    4: 'Body of corpus callosum', 5: 'Splenium of corpus callosum',  6: 'Fornix (column and body of fornix)',
    7: 'Corticospinal tract R',  8: 'Corticospinal tract L',  9: 'Medial lemniscus R'}
   df = regions_values(atlas_fp, maps_fp, subjects=subjects, labels=names.values())



