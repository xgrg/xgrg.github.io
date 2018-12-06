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
> **Note**: We will be using the [`pyxnat`](https://pypi.org/project/pyxnat/) library
> to make REST API calls from Python code.</div>

### Step 1: create subjects

```python
from pyxnat import Interface

config_file = '/home/grg/.xnat_bsc.cfg'
subjects = ['subject01', 'subject02', 'subject03']
project = 'MY_PROJECT'

# setup an XNAT connection
c = Interface(config=config_file)

# create subjects
for subject in subjects:

   uri =  '/data/projects/%s/subjects/%s'%(project, subject)

   response = c.put(uri)
   subject_uid = response.content
   print 'New subject %s created!' %subject_uid


```

### Step 2: create experiments

```python
experiments = {}
for subject in c.select.project(project).subjects():
     s = c.select.project(project).subject(subject.id())
     e = s.experiment('%s_MR2'%subject.label())

     options = {'xsiType':'xnat:mrSessionData'}
     e.create(**options)
     print 'New experiment %s created!' %e.id()
     experiments[subject] = e
```

### Step 3: create scans

```python
scans = {}
for subject, experiment in experiments.items():
     options = {'xsiType':'xnat:mrScanData',
                'type':'DWI',
                'series_description':'DWI',
                'quality':'usable'}
     sc = experiment.scan('1')

     sc.create(**options)     
     print 'New scan %s created!' %scan.id()
     scans[subject] = sc
```

### Step 4: create resources

```python
resources = {}
for subject, scan in scans.items():
    res = scan.resource('NIFTI')
    res.create()
    print 'New resource %s created!' %res.id()
    resources[subject.label()] = res
```

### Step 5: add files to just created resources

```python
# NIfTIs files given in order matching with subjects
files = ['subject01.nii', 'subject02.nii', 'subject03.nii']

for subject, filename in zip(subjects, files):    
    resource = resources[subject]

     f = resource.file(filename)
     response = f.put(src=filename, format='NIFTI', content='NIFTI',
       extract=False, overwrite=True)

     file_uid = response.content
     print 'File %s added!' %file_uid
```


`pyxnat` has a function to remove a resource from XNAT:

```python
uri = '/data/project/%s/subjects/%s/experiments/%s/'\
  %(project, subject_id, experiment_uid)
response = c.select(uri).delete(uri, delete_files=True)
```

The `delete_files` option deletes the files that come associated to the removed
resources.

Note that for security reasons, the URI should contain both the **subject's ID
and the experiment's ID** in order to proceed. Same goes for the **upload** step.

Many thanks to [Jordi Huguet](https://github.com/jhuguetn) from
[BarcelonaBeta](https://barcelonabrainimaging.org) for such valuable and
continuous help with this matter.
