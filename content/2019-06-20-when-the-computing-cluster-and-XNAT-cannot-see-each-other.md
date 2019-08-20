Title: When XNAT and the HPC cannot see each other...
Category: XNAT
Status: Published
Tags: xnat, python, pyxnat, freesurfer, hpc
Authors: Grégory Operto

This was written before XNAT releases its container service. XNAT can be configured so that processing jobs may be sent over a high performance computing system. Recent versions now also supports the use of containerization. We put up a "manual" to allow exporting jobs from XNAT in contexts where its container service is not available.


<!-- PELICAN_END_SUMMARY -->

The practical recipe is actually built around a sequence involving at most three nodes, namely the XNAT server (`X`), the processing unit (`Y`) and the local machine from where the recipe is operated (`Z`). The sequence can be summarized as follow:

* download some input data from `X` to `Y`, sometimes using `Z` as intermediate step
* build commands to be launched on `Y`
* run jobs on `Y` using any preferred/available job manager
* download processing results from `Y` to `Z` and push them to `X`.

This requires Python to be installed on `Z`.
The recipe is admittedly imperfect on many aspects, especially considering that it does not let XNAT manage the provenance of the processed data as it does with nominal workflows. Yet it allows to take advantage of additional computation resources while still making the results available on the XNAT instance.

This present example was based on actual previous experience where we had to run thousands of hippocampal subfield segmentation using FreeSurfer v6.0. In normal conditions, we have processing tasks handled by a fully-dedicated-but-average-sized individual workstation but in this particular case, *"outsourcing"* it to an HPC (or any other computing unit) would allow to not overwhelm it while still getting results in a reasonable time. Using containerization on the HPC would also mitigate known issues about discrepancy of results [across architectures and operating systems](https://www.frontiersin.org/articles/10.3389/fninf.2015.00012/full).

The recipe's code was put together in a Python module, provided for reference only (*read* "dirty - may explode"), that can be found [here](https://gitlab.com/xgrg/x2c). [x2c](https://gitlab.com/xgrg/x2c) stands for *XNAT-to-cluster*.

In summary it intends to work from CLI as follow:

```bash
x2c --config /path/to/xnat.cfg --experiment EXPERIMENT_ID --host COMPUTING_UNIT_ID --output /path/to/working_dir
```

It is based on the following commands, called sequentially:

```python
def fetch_from_xnat(config_file, files, experiment_id, path,  
        include_freesurfer=False, doit=False):
            ''' Downloads a given list of File instances from
            XNAT and stores them in a given path
            (/path/to/working_dir in the previous example)
            with names according to the experiment_id. Includes
            previous results from FREESURFER6 if needed.
            '''
```

```python
def rsync_to_hpc(host, path, experiment_id, dd, include_freesurfer=False,
            doit=False, clean=True):
    ''' Sends necessary resources to host (computing unit)
      including:
        - host definition (COMPUTING_UNIT_ID)
        - path to local data
        - experiment_id (EXPERIMENT_ID)
        - path to remote data (where to copy it)
        - should we copy previously generated FreeSurfer archive
        - should we remove the files after the transfer
        - should we do it for real (or just print commands)
    '''
```

```python
def singularity_cmd(dd, experiment_id, subject_label,
        singularity_fp, image_fn, reconall=False):
    ''' Builds a `singularity` command provided:
        - path to remote directory
        - experiment_id and subject_label
        - path to singularity executable
        - path to singularity image
        - include (or not) reconall step
    '''
```

```python
def hippo_zip(host, dd, experiment_id, subject_label):
    ''' Builds proper commands to build a zipfile with
    previously generated hippocampal subfields.
    '''
```

```python
def upload_subject(config, experiment, zipfile, resource_name):
  ''' Uploads a zipfile as a resource associated with a given
  experiment on an XNAT instance.
  '''
```

```python
def post_commands(host, dd, path, experiment_id, subject_label,
      config_file):
    ''' Prepares series of commands:
        - to build a zipfile archive with hippocampal subfields
        - transfer this archive back to local machine
        - upload it to XNAT
    This requires:
        - host definition
        - path to remote data
        - path to local data (where to download it)
        - experiment_id and subject_label
        - XNAT configuration file
    '''
```

The whole thing makes intensive use of [`pyxnat`](https://github.com/pyxnat/pyxnat) for obvious reasons. More information on [how to get started with `pyxnat`](http://xgrg.github.io/first-steps-with-pyxnat/).
