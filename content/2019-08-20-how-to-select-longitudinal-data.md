Title: How to select longitudinal data from XNAT
Category: XNAT
Status: Published
Tags: xnat, python, pyxnat
Authors: Grégory Operto


This is a short example showing how to identify subjects with multiple MR experiments on XNAT, for potential use in the context of a longitudinal analysis. Consider it as an extra tutorial for [`pyxnat`](http://github.com/pyxnat).

<!-- PELICAN_END_SUMMARY -->


As almost always, everything starts with creating an `Interface`.

```python
import pyxnat
x = pyxnat.Interface(config='/home/grg/.xnat_bsc.cfg')

# We start collecting experiments from a few projects
experiments = []
for p in ['ALFA_PLUS', 'ALFA_OPCIONAL']:
    # For each project, collect existing experiments
    # with information e.g. subject_label, scan date
    columns = ['subject_label', 'date']
    project_exp = x.array.experiments(project_id=p, columns=columns)
    # Add them to a big list
    experiments.extend(project_exp.data)

print('%s experiments found in both projects'%len(experiments))
```

For each experiment, retrieve info e.g. subject label, acquisition date, session ID. Then, create a list for each subject and store the information
in a dictionary.

```python
# For each experiment, retrieve info e.g. subject label,
# acquisition date, session ID.
subjects = {}
for e in experiments:
    subject_label = e['subject_label']
    mr_scandate = e['date']
    session_id = e['ID']
    project_id = e['project']

    # Create a list for each subject and store the information
    subjects.setdefault(subject_label, [])
    info = (session_id, mr_scandate, project_id)
    subjects[subject_label].append(info)

    # Now for each subject, we have the number of existing scans
    # and their acquisition dates
print(subjects['10010'])
```

Now we can filter the ones with more than one MR session.

```python
# Give me the ones with more than one timepoint
longitudinal = {}
for subject, sessions in subjects.items():
    if len(sessions) > 1:
        longitudinal[subject] = sessions

# Print the results
for each in list(longitudinal.items())[:5]:
    print(each)
print(len(longitudinal))
```

A Jupyter Notebook with the presented code can be found [there](https://github.com/xgrg/pyxnat/blob/nosetests/doc/notebooks/002%20-%20How%20to%20select%20longitudinal%20data.ipynb).
