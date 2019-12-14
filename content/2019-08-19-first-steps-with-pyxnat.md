Title: First steps with pyxnat
Category: XNAT
Status: Published
Tags: xnat, python, pyxnat
Authors: Grégory Operto


A couple of basic commands to get started with [`pyxnat`](http://github.com/pyxnat). This post quickly overviews the XNAT data model by the means of short examples, starting by creating a connection to a running instance. Documentation can be found [there](http://pyxnat.github.io/pyxnat).

<!-- PELICAN_END_SUMMARY -->

There are various ways to setup a connection to an XNAT server. They all
rely on the creation of a `pyxnat.Interface` object.

First by directly using some login credentials. Here the [XNAT CENTRAL public
instance](https://central.xnat.org) is taken as an example.

```python
import pyxnat
x = pyxnat.Interface(server='https://central.xnat.org',
                     user='USERNAME', password='PASSWORD')

projects = list(x.select.projects())
print(projects)
```

Another option is to store these in a configuration file and to pass it
to create the `Interface`.

```python
import pyxnat
x = pyxnat.Interface(config='/path/to/xnat_config.cfg')
```

The configuration file should be in JSON format and would look like this:

```python
{"server": "https://central.xnat.org",
 "user": "USERNAME",
 "password": "PASSWORD"}
```

It is also possible to create this configuration file from an existing `Interface`.

```python
interface = pyxnat.Interface(server='https://central.xnat.org',
                     user='USERNAME', password='PASSWORD')
interface.save_config('/path/to/xnat_config.cfg')
```



From there the `Interface` can be used e.g. to collect a list of existing
projects, or subjects from a given project.

```python
project = interface.select.project('xnatDownload')
subjects = list(project.subjects())
print(subjects)
```

Subjects have two types of identifiers, one that is an XNAT unique ID (see `id()` method) and a second one (see `label()` method).

```python
subject_labels = [e.label() for e in subjects]
print(subject_labels)
```

In the XNAT model subjects may have associated experiments (e.g. MR, PET, CT, etc.). Like subjects, experiments have two types of identifiers, IDs and labels. In the following example, we select a given subject (`sub-001`) in project `xnatDownload` and look for an experiment by its label (`sub-001_ses-01`). This example may be found on XNAT CENTRAL at this [URL](https://central.xnat.org/app/action/DisplayItemAction/search_element/xnat%3AmrSessionData/search_field/xnat%3AmrSessionData.ID/search_value/CENTRAL_E74609/popup/false/project/xnatDownload).

An experiment may be composed of multiple scans (e.g. corresponding to various MR sequences). Each scan has a `SeriesNumber` and a `SeriesDescription`, generally assigned at acquisition time by the scanner.
Here, we select a scan by its `SeriesNumber` and then ask for its `SeriesDescription` by querying on the `type` attribute.

```python
project = interface.select.project('xnatDownload')
experiment = project.subject('sub-001').experiment('sub-001_ses-01')
scan = experiment.scan('3')
print(scan.attrs.get('type'))
```

A scan typically has attached resources, such as `DICOM` directly coming from the scanner, or their `NIFTI` versions, `SNAPSHOTS`, etc. In the following case, we will take the first file from the `DICOM` collection of the previous
scan.

```python
resource = scan.resource('DICOM')
f = resource.files().first()
filename = f.label()

print(filename)
```

This final command allows to download the file to the local system.

```python
f.get(dest='/tmp/%s'%filename)
```

A Jupyter Notebook with the presented code can be found [there](https://github.com/xgrg/pyxnat/blob/nosetests/doc/notebooks/001%20-%20First%20steps%20with%20pyxnat.ipynb).
