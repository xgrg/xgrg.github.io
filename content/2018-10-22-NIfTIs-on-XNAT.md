Title: Pushing NIfTIs to XNAT
Category: XNAT
Status: Published
Tags: xnat, nifti, python
Authors: Grégory Operto

The primary data format with which XNAT works has been and is still DICOM. XNAT
can work with NIfTI but it generally has to be using secondary resources attached
to subjects, experiments or scans.

<!-- PELICAN_END_SUMMARY -->

This example shows how to get a dataset made of NIfTIs uploaded to XNAT without
their corresponding DICOM versions.

> <div style="padding:20px; text-align:justify; background-color:#222222">
> **Note**: We will be using the [`bxl`](https://pypi.org/project/bxl/) library
> to make all our REST API calls from Python code.</div>

### Step 1: create subjects

```python
from bxl import xnat
from bxl import utils

config_file = '/home/grg/.xnat_bsc.cfg'
subjects = ['subject01', 'subject02', 'subject03']

# setup an XNAT connection
c = utils.setup_xnat(config_file)

# create subjects
for subject in subjects:

   uri =  c.host + '/data/projects/MY_PROJECT/subjects/%s'%subject

   response = c._put_resource(URI=uri)
   subject_uid = response.content
   print 'New subject %s created!' %subject_uid

# build a dict with XNAT_IDs
subjects_dict = dict([(v['label'], e) \
  for e, v in c.get_subjects('MY_PROJECT').items()])
```

### Step 2: create experiments 

```python
experiments = {}
for subject in subjects.keys():
     xnat_id = subjects[subject]

     uri = c.host + '/data/projects/MY_PROJECT/subjects/%s/experiments/%s_MR1/'\
          %(xnat_id, subject)
     options = {'xsiType':'xnat:mrSessionData'}

     response = c._put_resource(URI=uri, options=options)
     experiment_uid = response.content
     print 'New experiment %s created!' %experiment_uid
     experiments[subject] = experiment_uid
```

### Step 3: create scans

```python
for subject, experiment_uid in experiments.items():
     xnat_id = subjects[subject]

     options = {'xsiType':'xnat:mrScanData',
                'type':'DWI',
                'series_description':'DWI',
                'quality':'usable'}
     uri = c.host + '/data/experiments/%s/scans/1/'%experiment_uid

     response = c._put_resource(URI=uri, options=options)
     scan_uid = response.content
     print 'New scan %s created!' %scan_uid
```

### Step 4: create resources

```python
for subject, experiment_uid in experiments.items():
    xnat_id = subjects[subject]

    uri = c.host + '/data/experiments/%s/scans/1/resources/NIFTI'%experiment_uid

    response = c._put_resource(URI=uri)
    resource_uid = response.content
    print 'New resource %s created!' %resource_uid
```

### Step 5: add files to just created resources

```python
# NIfTIs files given in order matching with alphabetically-sorted subjects
files = ['subject01.nii', 'subject02.nii', 'subject03.nii']

for subject, fp in zip(sorted(subjects.keys()), files):
     xnat_id = subjects[subject]

     uri = c.host + \
        '/data/experiments/%s/scans/1/resources/NIFTI/files/%s.nii.gz'\
        %(experiment_uid, subject)
     options = {'format':'NIFTI',
                'content':'NIFTI',
                'extract':'false',
                'overwrite':'true'} #optional

     response = c._put_file(URI=uri, filename=fp, options=options)
     file_uid = response.content
     print 'File %s added!' %file_uid
```


`bxl` has a function to remove a resource from XNAT:

```python
xnat_id = subjects[subject]
uri = c.host + '/data/project/MY_PROJECT/subjects/%s/experiments/%s/'%(xnat_id, experiment_uid)
response = c.delete_resource(uri, options={'removeFiles':True})
```

The `removeFiles` option deletes the files that come associated to the removed
resources.

Note that for security reasons, the URI should contain both the subject's ID
and the experiment's ID in order to proceed.

Many thanks to [Jordi Huguet](https://github.com/jhuguetn) from
[BarcelonaBeta](https://barcelonabrainimaging.org) for such valuable and
continuous help with this matter.
