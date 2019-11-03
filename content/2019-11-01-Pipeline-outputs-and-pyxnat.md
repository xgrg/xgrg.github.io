Title: Pipeline outputs and pyxnat
Category: XNAT
Status: Published
Tags: xnat, python, pyxnat
Authors: Grégory Operto

XNAT stands for _eXtensible Neuroimaging Archive Toolkit_ and as such, it may be
extended to meet some specific needs and host data of heterogeneous types.

<!-- PELICAN_END_SUMMARY -->

Among existing features XNAT is designed to host any generic collection of DICOM/NIfTI files and their associated derived resources. Interacting with the
data can be done mainly two ways: either graphically using the web application,
or through a REST API. In particular the [`pyxnat`](http://pyxnat.github.io/pyxnat)
library adds an extra layer over the REST API to allow interfacing an XNAT
instance in Python (see [First steps with `pyxnat`](http://xgrg.github.io/first-steps-with-pyxnat/)).

In XNAT, resources such as pipeline outputs (FreeSurfer results, SPM
  segmentations, etc.) may be stored as derived `Resources` under any imaging
  experiment. Such objects can then be queried and collected easily through the
  web app, the REST API or in Python, as follows:

```python
import pyxnat
central = pyxnat.Interface(server='https://central.xnat.org')
subject = central.select.project('nosetests3').subject('rs')
experiment = subject.experiment('rs_MR1')
resource = experiment.resource('FREESURFER6')
```

This object comes with functions for interacting with the `resource`, such as
iterating over files or downloading/uploading contents. However,
these objects have long remained totally agnostic of the contained data,
regardless of the pipeline. This was mainly due to the fact that such resources
 are highly instance-dependent, and pipeline implementation is bound to vary a
 lot from one center to another.

In the very last [`pyxnat`](http://pyxnat.github.io/pyxnat) release a couple of
days ago (version `1.2.1.0.post3`), we introduced a mechanism to tune these objects and allow adding custom functions for specific types of resources.

For instance, since this new release, one can now directly write:
```python
resource = experiment.resource('FREESURFER6')
aparc = resource.aparc()
aseg = resource.aseg()
```
and thus get access to FreeSurfer measurements.

Another example, with the ASHS pipeline for hippocampal subfield segmentation:
```python
resource = experiment.resource('ASHS')
volumes = resource.volumes()
```

Again, this would only work provided that corresponding resources respect a certain
naming and structure on XNAT. Here in this present example, FreeSurfer results
are stored in resources called `FREESURFER6` and the whole FreeSurfer folder
(named after the subject) is stored in the resource. Not having such resources
would just have no effect and the resources would be served with their default
basic functions.

Nevertheless, this mechanism has been implemented so as to get easily adapted to
local configurations, by editing/adding to a specific place in the library code.

Adding a custom function is done simply as follows.

In the folder `pyxnat/core/derivatives/`, edit any existing file or add a new
one (filename does not matter):

  - Define `XNAT_RESOURCE_NAME`. This variable names the XNAT resource which
  needs a custom function.
  - Write the custom function with `self` as first parameter (`self` will be
    the `pyxnat` `Resource` object).

If the resources which the custom function should be added has multiple names instead of a single one, their list may be provided under the variable
`XNAT_RESOURCE_NAMES`.

Example in `pyxnat/core/derivatives/freesurfer.py`:

```python
XNAT_RESOURCE_NAMES = ['FREESURFER6', 'FREESURFER6_HIRES']

def hippoSfVolumes(self, mode='T1'):
    import pandas as pd

    table = []
    files = list(self.files('*h.hippoSfVolumes-%s.v10.txt'%mode))
    for f in files:
        uri = f._uri

        res = self._intf.get(uri).text.split('\n')
        d1 = dict([each.split(' ') for each in res[:-1]])
        d2 = dict([('%s'%k, float(v)) \
                   for k,v in d1.items()])

        side = {'l':'left', 'r':'right'}[uri.split('/')[-1][0]]
        for region, value in d2.items():
            row = [side, region, value]
            table.append(row)

    columns = ['side', 'region', 'value']
    return pd.DataFrame(table, columns=columns)
```

Since then this mechanism has been leveraged in higher-level functions such as in
[`bx`](https://gitlab.com/xgrg/bx), e.g. for [collecting all numerical results from FreeSurfer over
an entire XNAT project](http://xgrg.github.io/bulk-downloading-resources-from-xnat) or [caching them on a local drive](http://xgrg.github.io/caching-freesurfer6-measurements).
