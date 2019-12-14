Title: Caching FreeSurfer measurements for faster access
Category: XNAT
Status: Published
Tags: xnat, python, pyxnat, freesurfer
Authors: Grégory Operto

We love being able to access the freshest data directly from our XNAT platform.
By querying it from Jupyter notebooks, we make sure to have full control on the
resource provenance. But let's admit it, beyond a couple of thousands of
participants, collecting - and re-collecting - the
 data every time can start to get rather time-consuming.


<!-- PELICAN_END_SUMMARY -->

This example shows how to use a basic _caching_ system to avoid downloading
multiples times the same data (here, `aseg` or `aparc` features) from an XNAT
platform by storing/accessing it in/from local files with the exact same piece
of code. The principle is the following: the system will look for the data in _cache_
files in priority; if no _cache_ files can be found, then the data will be
downloaded and cached for future access.

> <div style="padding:20px; text-align:justify; background-color:#222222">
> **Note**: this example is far from perfect. For instance, it does not check
> whether the data may have been updated server-side and only relies on the
> existence of previously saved files.</div>

The reader is invited to refer to this [script](https://gitlab.com/xgrg/bx/blob/ef83f4c45ec987d5bd1fc42510e25ff6cdebdbf7/bx/cache.py) to understand the
following section.

The function `cache_freesurfer6()` works with a [`pyxnat`](https://pyxnat.github.io/pyxnat)
`Interface` instance and a reference to any project from an XNAT platform.

For example, consider the following.

```python
from cache import cache_freesurfer6
import pyxnat

project_id = 'ALFA'
c = pyxnat.Interface(config='/home/user/.xnat.cfg')
(aseg ,) = cache_freesurfer6(c, project_id, measurements=['aseg'])
etiv = aseg.query('measurement == "Volume_mm3" & region == "eTIV"')
```

The first execution will give this:

```
INFO:root:MD5: 34c1660a924c32c065f4c8a51fc6a99a
INFO:root:Saving /tmp/bxcache_34c1660a924c32c065f4c8a51fc6a99a/bxcache_aseg_20190619_125621.xlsx
INFO:root:Elapsed time: 0:05:54
```

A second execution will generate the following output:

```
INFO:root:MD5: 34c1660a924c32c065f4c8a51fc6a99a
INFO:root:Found cache 20190619_125621
INFO:root:Loading ['/tmp/bxcache_34c1660a924c32c065f4c8a51fc6a99a/bxcache_aseg_20190619_125621.xlsx']
INFO:root:Elapsed time: 0:00:03
```

The two executions will return the same `aseg` features (provided there was no
  update of the data between both). In case there was an update, it is possible
  to force rewriting the cache with the `force` option.

This piece of code is a part of the [`bx`](https://gitlab.com/xgrg/bx) Python module, which is used at
[BarcelonaBeta](https://barcelonabrainimaging.org) to facilitate bulk downloads
from XNAT. It was built onto [`pyxnat`](https://github.com/xgrg/pyxnat/tree/bbrc)
(`bbrc` branch).
