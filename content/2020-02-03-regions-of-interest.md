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
 > in a module called [roistats](https://github.com/xgrg/roistats), presented here. </div>

##  Collecting mean values from atlas regions

`roistats.collect` submodule has a function `roistats_from_maps(images, atlas_fp)`
which takes
