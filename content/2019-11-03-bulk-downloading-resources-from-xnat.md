Title: Bulk downloading resources from XNAT
Category: XNAT
Status: Published
Tags: xnat, python, pyxnat
Authors: Grégory Operto

Interacting with the data on XNAT can be done mainly two ways: either graphically using the web application, or through a REST API. While the former is suited for
all profiles, the latter is intended for a more technical category of users.

<!-- PELICAN_END_SUMMARY -->

The [`pyxnat`](http://pyxnat.github.io/pyxnat)
library adds an extra layer over the REST API to allow interfacing an XNAT
instance in Python (see [First steps with `pyxnat`](http://xgrg.github.io/first-steps-with-pyxnat/)).
This can be of great help to automate bulk operations e.g. downloading large
collections of data, populating projects or any type of systematic task that
would otherwise require lots of clicks using the web app.

Between "all clicks" and "all code" lies a large gray zone with users somewhere between the hardcore Python gurus and the bash rookies. For this special category
(i.e. the majority in the research group I belong to) we developed an
intermediate tool called [bx](https://gitlab.com/xgrg/bx) (for BarcelonaBeta +
  XNAT) covering some of the most frequent tasks (based on reports) as for
  instance:

- download NIfTI files of a given sequence over a project
- download SPM/FreeSurfer outputs over a projects
- download an Excel table with all FreeSurfer/ASHS measurements over a project
- download a table with acquisition dates from an entire project
- in general, _downloading any given resource over an entire project_.

The tool is used as a single command followed by options as in this example:

```
bx freesurfer6 aseg <RESOURCE_ID>
```

where `RESOURCE_ID` is a reference either to a experiment or a project. Running
the command will execute the proper REST calls to achieve the operation. Of
course, this will strongly depend on how pipelines are mounted in the specific
XNAT instance (how resources are named and how files are structured in them).
Still, the process will rely on intermediate calls to [`pyxnat`](http://pyxnat.github.io/pyxnat), hence enabling the implementation of
new commands/options and/or the adaptation of existing ones (see [example here](https://gitlab.com/xgrg/bx/blob/master/bx/ashs.py)).

The tool also comes with a Python module `bx.cache` which allows to maintain a local
cached version of FreeSurfer/ASHS measurements and avoid potential long
repetitive downloads, in particular when working with Jupyter Notebooks.
More information on this specific module can be found in [Caching FreeSurfer
measurements for faster access](http://xgrg.github.io/caching-freesurfer6-measurements).
