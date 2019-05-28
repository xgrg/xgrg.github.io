Title: Importing external resources to XNAT
Category: XNAT
Status: Published
Tags: xnat, nifti, python
Authors: Grégory Operto

We tend to give general preference to data coming from local "_XNAT-native_"
 workflows. Yet sometimes some factors (e.g. related to computational power,
   software availability) may require us to import resources from external,
   less controlled, data sources.

<!-- PELICAN_END_SUMMARY -->

This example shows how to get external archives imported to an XNAT instance
as additional resources to MR experiments. In this present case these archives
will consist of FreeSurfer outputs.

> <div style="padding:20px; text-align:justify; background-color:#222222">
> **Note**: The interested reader may refer to [Pushing NIfTIs to XNAT](http://xgrg.github.io/NIfTIs-on-XNAT/)
> or [Pushing bulk legacy data to XNAT](http://xgrg.github.io/pushing-bulk-legacy-data-to-XNAT/)
> for more contents on how to upload external data to XNAT.</div>

### Step 1: prepare archive files with the resources to be imported

FreeSurfer `recon-all` outputs generally follow a standard file organization
under a parent folder named after the subject (stored in the `SUBJECTS_DIR` root
 folder). In this example, we first create a ZIP file for every subject at the
 level of their corresponding individual folder.

> For each subject:
>
> `cd $SUBJECTS_DIR; zip -r $SUBJECTNAME_FREESURFER6.zip $SUBJECTNAME`

The ZIP file will contain one single folder (carrying the subject's ID) which
will contain the usual FreeSurfer folders (`mri`, `stats`, `scripts`, etc.).

For the next step we will need a Python dictionary `zipfiles` giving for every
subject the path to the corresponding ZIP file.

Example:
```
zipfiles = {'subject01': '/path/to/subject01_FREESURFER6.zip'}
```

### Step 2: create blank project/subjects/experiments and assign resources

In case the subjects/experiments already exist, the following code will need to
be adapted with proper values for variables `subjects` and `experiments`.

```python
from pyxnat import Interface

config_file = '/home/grg/.xnat_bsc.cfg'
subjects = ['subject01', 'subject02', 'subject03']
project = 'MY_PROJECT'

# setup an XNAT connection
c = Interface(config=config_file)
p = c.select.project(project)
p.create()
experiments = {}

# create subjects
for subject in subjects:
   s = p.subject(subject)
   s.create()
   e = s.experiment('%s_MR1'%subject) # experiment will be named after subject
   e.create()

   r = e.resource('FREESURFER6')
   zipfile = zipfiles[subject] # needs to be previously built
   r.put_zip(zipfile, format=None, content=None, tags=None)

c.disconnect()
```

The ZIP files will be extracted online and the contents will appear as
additional resources of their corresponding experiments.

### Step 3 (only at [BarcelonaBeta](https://barcelonabrainimaging.org)): run FreeSurfer validator

Since we are importing FreeSurfer resources, it may be advised to launch a
FreeSurfer Validator which will run a series of checks over the imported data.

To do so, make sure the corresponding XNAT pipeline (`freesurfer_validation`) is
properly activated in the project.

The validator **expects** the resource's name to be `FREESURFER6` and its structure
to follow the one described earlier (folder with subject's ID then FreeSurfer's
folders).

Once completed, there will be a new resource `BBRC_VALIDATOR` to the experiment
with both the JSON and the PDF report resulting from this validation.

### Step 4: collect all measurements in a single Excel table using `bx`

To collect all produced measurements from XNAT directly into a single Excel
file, one may use [bx](https://gitlab.com/xgrg/bx).

Once again, the tool would expect resource names to be `FREESURFER6` and their
 structure to follow the one described earlier (folder with subject's ID then
 FreeSurfer's folders).

 Then using the following command:

 ```
 bx freesurfer6 aseg MY_PROJECT
 ```

This will generate an Excel table (saved in `/tmp` by default) with all the `aseg`
stats (also works with `aparc` or `hippoSfVolumes` if available).
