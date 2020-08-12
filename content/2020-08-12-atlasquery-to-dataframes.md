Title: FSL/TBSS: Determine anatomical labels from clusters using Python
Category: TBSS
Status: Published
Tags: python, tbss
Authors: Grégory Operto


After some time building more and more contrast maps with FSL/TBSS, I needed some 
way to compile information - anatomical in particular - from clusters in a thresholded map. The typical information that may then be reported in a paper. 
I was probably not the first one to look for this (as suggested [here](https://www.ibic.washington.edu/wiki/download/attachments/26869797/ibicMakeManual20160216.pdf)) but I could not find any tool (like a [Nipype](https://nipype.readthedocs.io/en/latest/) interface) or recipe suited to my needs. Only later I found out about [AtlasReader](https://github.com/miykael/atlasreader) which creates activation tables with some extra `nilearn`-type snapshots. It also seems that [fslpy](https://git.fmrib.ox.ac.uk/fsl/fslpy/-/blob/master/fsl/scripts/atlasq.py) has a wrapper to FSL's `atlasquery`, which does what I want, except that I wanted something closer to FSL's `autoaq` *and* possibility to get the outputs as DataFrames.

FSL/TBSS comes indeed with that useful command ([`atlasquery`](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/Atlasquery)) which returns the name and proportions of the regions from any given reference atlas (among the ones supplied with FSL) that would show an overlap with clusters from any binary map. 

Hence the following Python functions (named after the original commands) are just wrappers around `atlasquery` and `autoaq` and convert their outputs to `pandas` DataFrames. 

See the full code [there](https://github.com/xgrg/tbss/blob/master/tbss/__init__.py).

```python
data = atlasquery('/tmp/tmpsi1gyceh.nii.gz', 
                  'JHU White-Matter Tractography Atlas')
data.sort_values(by='pc', ascending=False).head()
```

> | tract                                  |     pc |
> |:---------------------------------------|-------:|
> | Forceps minor                          | 5.2468 |
> | Inferior longitudinal fasciculus L     | 1.794  |
> | Inferior fronto-occipital fasciculus L | 1.7061 |
> | Anterior thalamic radiation L          | 1.6814 |
> | Superior longitudinal fasciculus L     | 1.4276 |

The input map is assumed to be binary. If it is not, then one can use `autoaq` 
and give a specific threshold for the input map (default: 0.95 (equivalent to `p<0.05`)). Two dataframes will be returned as original results come in [multiple
 sections](https://brainder.org/tag/autoaq/).


```python
data = autoaq('/path/to/map_FA_tfce_corrp_tstat3.nii.gz', 
              'JHU White-Matter Tractography Atlas', 
              thr=0.95)
data[0]  
```

> |   ClusterIndex |   Voxels |   MAX |   MAX X (mm) |   MAX Y (mm) |   MAX Z (mm) |   COG X (mm) |   COG Y (mm) |   COG Z (mm) | pc_tract                         |
> |---------------:|---------:|------:|-------------:|-------------:|-------------:|-------------:|-------------:|-------------:|:---------------------------------|
> |              1 |    25356 | 0.988 |           14 |           27 |           16 |        -7.98 |        -5.61 |         16.5 | 9% Anterior thalamic radiation L |


```python
data[1].sort_values(by='pc', ascending=False).head()
```

> |   ClusterIndex | tract                                  |     pc |
> |---------------:|:---------------------------------------|-------:|
> |              1 | Forceps minor                          | 5.2026 |
> |              1 | Inferior longitudinal fasciculus L     | 1.8074 |
> |              1 | Inferior fronto-occipital fasciculus L | 1.7149 |
> |              1 | Anterior thalamic radiation L          | 1.6879 |
> |              1 | Superior longitudinal fasciculus L     | 1.438  |


These two commands have been integrated to the [little Python module](https://github.com/xgrg/tbss) that I use for TBSS-related work.