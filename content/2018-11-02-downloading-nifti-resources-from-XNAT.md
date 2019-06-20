Title: Downloading NIfTI resources from XNAT
Category: XNAT
Status: Published
Tags: xnat, nifti, python, pyxnat
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
> **Note**: We will be using the [`pyxnat`](https://pypi.org/project/pyxnat/) library
> to make REST API calls from Python code.</div>

```
config_file = '/home/grg/git/bbrc-validator/.xnat.cfg'
dest_dir = '/tmp/'
subjects = ['SUBJ_003']
project = 'testenv'
scantypes = {'DWI': ['DWI_ALFA1'],
             'rDWI': ['rDWI_ALFA1']}

import logging as log
from pyxnat import Interface
import os.path as op
log.getLogger().setLevel(log.INFO)
log.info('* configuration file: %s'%config_file)

c = Interface(config=config_file)
experiments_id = {}
subjects_id = {}

# Fetching subjects from project
subjects_pr = c.select.project(project).subjects()
subjects_id = [e for e in subjects_pr if e.label() in subjects]

for subject in subjects_id:
    log.info('Project: %s Subject: %s'%(project, subject.label()))

    # For each subject we assume there is one MRsession only
    exp = c.array.experiments(project_id=project, subject_id=subject.id()).data
    exp_id = exp[0]['ID']

    # Fetching scans
    scans = c.array.scans(experiment_id=exp_id,
      columns=['xnat:mrscandata/type']).data
    for m, st in scantypes.items():
        items = [sc['xnat:mrscandata/id'] for sc in scans \
                 if sc['xnat:mrscandata/type'] in st]
        log.info('Type %s: %s'%(m, items))
        if len(items) == 1:
             # Building the NIFTI resource URL
             res = [e for e in c.select.experiment(exp_id).scan(items[0]).resources()\
                if e.label() == 'NIFTI']

             # Downloading it             
             log.info('* Downloading %s in %s...(%s)'\
              %(subject.label(), op.join(dest_dir, e.id()), m))
             res = res[0].get(dest_dir)

        else:
            log.info('Found duplicates. %s'%items)
```

Many thanks to [Jordi Huguet](https://github.com/jhuguetn) from
[BarcelonaBeta](https://barcelonabrainimaging.org) for his valuable and
continuous help with this matter.
