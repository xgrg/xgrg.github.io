Title: Collecting image statistics from Regions-of-Interest over many subjects
Category: Python
Status: Published
Tags: python, image
Authors: Grégory Operto

Collecting basic image statistics (_e.g._ mean, std) from ROIs over a set of images can be done easily in Python.

<!-- PELICAN_END_SUMMARY -->

**EDIT (23-11-2018): check [roistats](https://github.com/xgrg/roistats) for a
module version of this code**

See the example in this [**Jupyter Notebook**](https://github.com/xgrg/alfa/blob/master/notebooks/Collecting%20image%20statistics%20from%20Regions-of-Interest%20over%20many%20subjects.ipynb)

	import numpy as np
	import nibabel as nib
	from glob import glob
	import pandas as pd
	from joblib import Parallel, delayed

	def roistats_from_map(map_fp, atlas, func):
	     m = np.array(nib.load(map_fp).dataobj)
	     n_labels = list(np.unique(atlas))
	     n_labels.remove(0)
	     label_values = [func(m[atlas==label]) for label in n_labels]
	     return label_values

	def roistats_from_maps(atlas_fp, maps_fp, subjects=None, labels=None,
		func=np.mean, n_jobs=7):

	     atlas_im = nib.load(atlas_fp)
	     atlas = np.array(atlas_im.dataobj)

	     n_labels = list(np.unique(atlas))
	     n_labels.remove(0)

	     df = Parallel(n_jobs=n_jobs, verbose=1)(\
	         delayed(roistats_from_map)(maps_fp[i], atlas, func)\
	         for i in xrange(len(maps_fp)))

	     columns = labels if not labels is None \
	             else [int(e) for e in n_labels]
	     res = pd.DataFrame(df, columns=columns)

	     res['subject'] = xrange(len(maps_fp)) if subjects is None else subjects
	     res = res.set_index('subject')

	     return res

`roistats_from_maps` takes a path to the label map defining the ROIS and a
list of filepaths to the images to compute the stats from. `roistats_from_map` returns
a list of values from one single map, while `roistats_from_maps` parallelizes it
(using [joblib](https://pythonhosted.org/joblib/)) over images and compiles the
returned rows into one single table, adding it a list of subject identifiers
(if argument `subjects` is given) and naming the columns with `labels` (if given).

By default, the mean is computed for every region but any other NumPy function
can be passed as `func` argument. Last but not least, is used for parallel processing.

Example:
----------

	:::python
	atlas_fp = '/path/to/rois.nii.gz'
	maps_fp = glob('/path/to/images*.nii.gz')
	subjects = [10538, 12252, 55708, 12121, 11015]
	names = {1: 'Middle cerebellar peduncle', 2: 'Pontine crossing tract',
	  	3: 'Genu of corpus callosum', 4: 'Body of corpus callosum',
		5: 'Splenium of corpus callosum',  6: 'Fornix',
		7: 'Corticospinal tract R',  8: 'Corticospinal tract L',
		9: 'Medial lemniscus R'}

	df = roistats_from_maps(atlas_fp, maps_fp, subjects=subjects, labels=names.values())
	#df.to_excel('/path/to/excelfile.xls')


Will return a table like:

|         | Middle cerebellar peduncle | Pontine crossing tract | Genu of corpus callosum | Body of corpus callosum | Splenium of corpus callosum | Fornix   | Corticospinal tract R | Corticospinal tract L | Medial lemniscus R |
|---------|----------------------------|------------------------|-------------------------|-------------------------|-----------------------------|----------|-----------------------|-----------------------|--------------------|
| subject |                            |                        |                         |                         |                             |          |                       |                       |                    |
| 10538   | 0.000817                   | 0.000895               | 0.000757                | 0.000818                | 0.000833                    | 0.000849 | 0.000819              | 0.000834              | 0.000716           |
| 12252   | 0.000850                   | 0.000896               | 0.000719                | 0.000816                | 0.000817                    | 0.000850 | 0.000843              | 0.000834              | 0.000743           |
| 55708   | 0.000853                   | 0.000929               | 0.000732                | 0.000851                | 0.000795                    | 0.000922 | 0.000839              | 0.000872              | 0.000786           |
| 12121   | 0.000842                   | 0.000926               | 0.000810                | 0.000846                | 0.000826                    | 0.000868 | 0.000810              | 0.000822              | 0.000723           |
| 11015   | 0.000847                   | 0.000879               | 0.000805                | 0.000877                | 0.000856                    | 0.000839 | 0.000814              | 0.000792              | 0.000831           |
