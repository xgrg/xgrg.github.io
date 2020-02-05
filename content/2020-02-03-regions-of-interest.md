Title: ROI-based analysis in neuroimaging: a tutorial in Python
Category: Image
Status: Draft
Tags: image, python
Authors: Grégory Operto



<!-- PELICAN_END_SUMMARY -->

As hypotheses in neuroimaging studies are often stated in terms of brain
structures, analyses based on Regions-on-Interest (ROIs) allow to focus
 over a number of parcels with homogeneous characteristics. Two approaches
 are generally available, as two opposite ways of addressing anatomical variability.

  - One way consists in warping all the subjects to a common
reference space and using ROIs defined from a brain atlas.
  - The other one consists in delineating ROIs individually in every subject,
  e.g., using segmentation algorithms.  Resulting objects are likely to be closer
  to the individual anatomical truth, and improve sensitivity by focusing on
  the signal of interest, as compared to voxel-based methods.

ROIs are thus often defined over anatomical data and then used to filter the
 signal from other image modalities.

 ## TL;DR

 > <div style="padding:20px; text-align:justify; background-color:#222222">
 > This post describes an end-to-end analysis workflow based on
 > regions-of-interest. Such workflows rely on typical operations
 > e.g. extracting values, merging them with covariates, plotting, performing some
 > linear regressions or group comparisons, which have been turned to Python code
 > in a package called [roistats](https://github.com/xgrg/roistats), presented here. </div>

##  Collecting mean values from atlas regions

`roistats.collect` module has a function `roistats_from_maps(images, atlas_fp)`
which takes a set (`images`) of images (their file paths) and `atlas_fp`, the
 path to a *ROI volume* (i.e. a volume with integer labels defining areas of
   interest [and 0 elsewhere]). All images should be coregistered in the same
   space (e.g. MNI). The ROI volume may thus come from an atlas, as the ones
   from the [`nilearn.datasets`](https://nilearn.github.io/modules/reference.html#module-nilearn.datasets)
  module.

In this example, let us generate some maps (N=50) with some random values over an
MNI brain mask. They will be like our individual (subject-level) maps. You may
use your own maps directly.

#### Generating random maps (optional)
```python

import tempfile
from nilearn import datasets
from nilearn import image
import numpy as np
images = []

atlas = datasets.load_mni152_brain_mask()

# Generate 50 random maps
for i in range(0, 50):
    d = np.random.rand(*atlas.dataobj.shape) * atlas.dataobj
    im = image.new_img_like(atlas, d)
    im = image.smooth_img(im, 5)
    _, f = tempfile.mkstemp(suffix='.nii.gz')
    im.to_filename(f)
    images.append(f)

from nilearn import plotting as npl
name = 'cort-maxprob-thr50-2mm'
atlas_fp = datasets.fetch_atlas_harvard_oxford(name)['maps']

for each in images[:3]:
    npl.plot_roi(atlas_fp, bg_img=each)
```

This [gist](https://gist.github.com/xgrg/3405bbe95f6aa589ac5dfbfb9843c73f)
shows the documented execution of this part.

#### Collecting values

```python
from roistats import collect
from roistats import
df = collect.roistats_from_maps(images, atlas_fp, subjects=None)


df = df.rename(columns=labels)

df['group'] = df.index
df['age'] = df.apply (lambda row: random.random()*5+50, axis=1)
df['group'] = df.apply (lambda row: row['group']<len(df)/2, axis=1)
df['index'] = df.index
