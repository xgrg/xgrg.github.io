Title: Downloading NIfTI resources from XNAT
Category: XNAT
Status: Published
Tags: xnat, nifti, python
Authors: Grégory Operto

It is quite common that we use XNAT to download a bunch of NIfTIs to run some
external analysis.

<!-- PELICAN_END_SUMMARY -->

This generic example shows how to download NIfTI resources from an XNAT instance.
In this context, NIFTI resources are stored at the _scan_ level
(`subject`/`experiment`/`scan`).

In this example, for every subject of a given list `subjects`, we need to
 download two sequences (their `SeriesType` being _`DWI_ALFA1`_ and
   _`rDWI_ALFA1`_ but may be anything else).


> <div style="padding:20px; text-align:justify; background-color:#222222">
> **Note**: We will be using the [`bxl`](https://pypi.org/project/bxl/) library
> to make all our REST API calls from Python code.</div>

```
config_file = '/home/grg/git/bxl/.xnat.cfg'
dest_dir = '/tmp/test'
subjects = ['SUBJ_003']
projects = 'testenv'
scantypes = {'DWI': ['DWI_ALFA1'],
             'rDWI': ['rDWI_ALFA1']}

import logging as log
from bxl import utils
import os.path as op
log.getLogger().setLevel(log.INFO)
log.info('* configuration file: %s'%config_file)

c = utils.setup_xnat(config_file)
experiments_id = {}
subjects_id = {}

# Fetching subjects from project
subjects_pr = c.get_subjects(project)
sid = {v['label'] : k for k, v in subjects_pr.items()}
for e in subjects:
    if e in sid.keys():
        subjects_id[e] = sid[e]

for k, v in subjects_id.items():
    # For each subject we assume there is one MRsession only
    experiments = c.get_subject_experiments(project, v)
    exp_id = experiments.items()[0][0]

    # Fetching scans
    options = {'columns': 'ID,type'}
    scans = c.get_mrscans(exp_id, options)

    log.info('Project: %s Subject: %s'%(project, k))

    for m, st in scantypes.items():
        items = [v['URI'] for e, v in scans.items() \
                    if v['type'] in st]
        log.info('Type %s: %s'%(m, items))
        if len(items) == 1:
             # Building the NIFTI resource URL
             url = c.host + items[0] + '/resources/NIFTI/files'
             # Fetching the URI of the first contained file
             uri = c.host + c._query_data(url)[0]['URI']     

             # Downloading it
             fp = op.join(dest_dir, '%s_%s.nii.gz'%(k, m))
             log.info('* Downloading %s...(%s)'%(k, m))
             res = c.download_resource(uri)
             log.info('* Saving %s...'%fp)
             with open(fp, 'w') as w:
                 w.write(res)       
        else:
            log.info('Found duplicates.')

```

Many thanks to [Jordi Huguet](https://github.com/jhuguetn) from
[BarcelonaBeta](https://barcelonabrainimaging.org) for his valuable and
continuous help with this matter.
