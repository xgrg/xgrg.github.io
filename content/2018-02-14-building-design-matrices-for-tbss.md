Title: Building design matrices for TBSS Randomise
Category: Python
Status: Published
Tags: python, tbss
Authors: Grégory Operto

Creating design matrices by hand for TBSS can be done in different ways
(explained
[here](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/GLM/CreatingDesignMatricesByHand)),
either using the FSL Wizard Gui or exporting it from a text file or an Excel
table.

<!-- PELICAN_END_SUMMARY -->

A design matrix in TBSS is nothing but another text file using its own (Vest)
format.
This shows how to make one out of any generic piece of tabulated data
in Python.

```python
def build_tbss_matrix(df):
      ''' Returns a TBSS-ready design matrix'''

      covlist = df.columns
      mat = ['/NumWaves %s'%len(covlist)]
      mat.append('/NumPoints %s'%len(df))
      mat.append('/Matrix')
      for row_index, row in df.iterrows():
	  s1 = ' '.join([str(row[e]) for e in covlist])
	  mat.append(s1)

      return '\n'.join(mat)
```

#### Example:

```python
  import pandas as pd
  fp = '/tmp/data1.xls'
  data = pd.read_excel(fp)
  data.head()
```


> |   |    age    | gender | centiloids |
> |:-:|:---------:|:------:|:----------:|
> | 0 | 63.422313 |    2   |    -7.62   |
> | 1 | 54.757016 |    1   |    -1.84   |
> | 2 | 50.390144 |    2   |    -0.16   |
> | 3 | 54.151951 |    1   |    -4.12   |
> | 4 |  52.87885 |    1   |   -17.65   |
>

```python
mat = build_tbss_matrix(data)
print(mat)
```

```
/NumWaves 3
/NumPoints 114
/Matrix
63.4223134839151 2.0 -7.62
54.757015742642 1.0 -1.84
50.3901437371663 2.0 -0.16
54.1519507186858 1.0 -4.12
52.8788501026694 1.0 -17.65
...
```

## Application to contrasts:

```python
def tbss_main_effect_contrasts(covlist):
    con = []
    for i, each in enumerate(covlist):
        c = [0] * len(covlist)
        c[i] = 1
        con.append(('%s(+)'%each, list(c)))
        c[i] = -1
        con.append(('%s(-)'%each, c))
    return con
```

This function will build a list of contrasts, two per
covariable in the design matrix (passed as argument `covlist`),
corresponding to the _main effect_ of each variable in both positive
and negative directions.

```python
  import pandas as pd
  fp = '/tmp/data1.xls'
  data = pd.read_excel(fp)
  covariates = list(data.columns)
  contrasts = tbss_main_effect_contrasts(covariates)
  print(contrasts)
```

```
[('age(+)', [1, 0, 0]),
 ('age(-)', [-1, 0, 0]),
 ('gender(+)', [0, 1, 0]),
 ('gender(-)', [0, -1, 0]),
 ('centiloids(+)', [0, 0, 1]),
 ('centiloids(-)', [0, 0, -1])]
```

In the same approach as with the design matrix, the result can be easily
converted into a text file ready to give to TBSS.

```python
def build_tbss_contrasts(contrasts):
    con = ['/NumWaves %s'%len(contrasts[0][1])]

    for i, (name, contrast) in enumerate(contrasts):
        con.append('/ContrastName%s %s'%(i+1, name))
    nb_contrasts = len(contrasts)
    con.append('/NumContrasts %s'%str(nb_contrasts))
    con.append('/Matrix')
    for i, (name, c) in enumerate(contrasts):
        con.append(' '.join([str(each) for each in c]))

    return '\n'.join(con)
```

#### Example (cont.):
```python
con = build_tbss_contrasts(contrasts)
print(con)
```

```
/NumWaves 3
/ContrastName1 age(+)
/ContrastName2 age(-)
/ContrastName3 gender(+)
/ContrastName4 gender(-)
/ContrastName5 centiloids(+)
/ContrastName6 centiloids(-)
/NumContrasts 6
/Matrix
1 0 0
-1 0 0
0 1 0
0 -1 0
0 0 1
0 0 -1
```

### Pairwise comparisons:

The following kind of code can be used to include 1-vs-1 contrasts in addition
to the main effects.

```python
def tbss_2vs2_contrasts(var, covlist):
    import itertools
    con = []
    for i, j in itertools.permutations(var, 2):
        c = [0] * len(covlist)
        c[covlist.index(i)] = 1
        c[covlist.index(j)] = -1
        con.append(('%s>%s'%(i,j), c))
    return con
```

#### Example:

```python
  import pandas as pd
  fp = '/tmp/data2.xls'
  data = pd.read_excel(fp)
  data.head()

```

> |   | apoe | age       | gender | centiloids |
> |---|------|-----------|--------|------------|
> | 0 | 0    | 63.422313 | 2      | -7.62      |
> | 1 | 0    | 54.757016 | 1      | -1.84      |
> | 2 | 2    | 50.390144 | 2      | -0.16      |
> | 3 | 0    | 54.151951 | 1      | -4.12      |
> | 4 | 0    | 52.878850 | 1      | -17.65     |

The design matrix would be:

```python
mat = build_tbss_matrix(data)
print(mat)
```

```
/NumWaves 6
/NumPoints 114
/Matrix
63.4223134839151 2.0 -7.62 -7.62 -0.0 -0.0
54.757015742642 1.0 -1.84 -1.84 -0.0 -0.0
50.3901437371663 2.0 -0.16 -0.0 -0.0 -0.16
54.1519507186858 1.0 -4.12 -4.12 -0.0 -0.0
52.8788501026694 1.0 -17.65 -17.65 -0.0 -0.0
...
```
Imagine that we are interested in the interaction between the two variables
`centiloids` (continuous) and `apoe4` (categorical [0,1,2]).

```python
def build_interaction(df, var, categ_var):
    '''Adds columns to a DataFrame with the interaction between a variable and
    a categorical variable.'''

    groups = np.unique(df['%s'%categ_var].values).tolist()
    for i, grp in enumerate(groups):
        apo = pd.DataFrame(df[categ_var] == grp, dtype=np.int)
        apocol = '%s%s'%(categ_var, groups[i])
        df[apocol] = apo
        intercol = '%s%s'%(var, groups[i])
        df[intercol] = df.apply(lambda row: row[apocol]*row[var], axis=1)
        del df[apocol]
    return df
```

```python
data = build_interaction(data, 'centiloids', 'apoe4')
del data['apoe4']
data.head()
```

> |   | age       | gender | centiloids | centiloids0 | centiloids1 | centiloids2 |
> |---|-----------|--------|------------|-------------|-------------|-------------|
> | 0 | 63.422313 | 2      | -7.62      | -7.62       | -0.0        | -0.00       |
> | 1 | 54.757016 | 1      | -1.84      | -1.84       | -0.0        | -0.00       |
> | 2 | 50.390144 | 2      | -0.16      | -0.00       | -0.0        | -0.16       |
> | 3 | 54.151951 | 1      | -4.12      | -4.12       | -0.0        | -0.00       |
> | 4 | 52.878850 | 1      | -17.65     | -17.65      | -0.0        | -0.00       |

This will generate the contrasts for the main effects and the
`apoe4 x centiloids` interaction:

```python
covariates = list(data.columns)
con = tbss_main_effect_contrasts(covariates)
pair_con = tbss_2vs2_contrasts(['centiloids0', 'centiloids1', 'centiloids2'], covariates)
con.extend(pair_con)
contrasts = build_tbss_contrasts(con)
print(contrasts)
```

```
/NumWaves 6
/ContrastName1 age(+)
/ContrastName2 age(-)
/ContrastName3 gender(+)
/ContrastName4 gender(-)
/ContrastName5 centiloids(+)
/ContrastName6 centiloids(-)
/ContrastName7 centiloids0(+)
/ContrastName8 centiloids0(-)
/ContrastName9 centiloids1(+)
/ContrastName10 centiloids1(-)
/ContrastName11 centiloids2(+)
/ContrastName12 centiloids2(-)
/ContrastName13 centiloids0>centiloids1
/ContrastName14 centiloids0>centiloids2
/ContrastName15 centiloids1>centiloids0
/ContrastName16 centiloids1>centiloids2
/ContrastName17 centiloids2>centiloids0
/ContrastName18 centiloids2>centiloids1
/NumContrasts 18
/Matrix
1 0 0 0 0 0
-1 0 0 0 0 0
0 1 0 0 0 0
0 -1 0 0 0 0
0 0 1 0 0 0
0 0 -1 0 0 0
0 0 0 1 0 0
0 0 0 -1 0 0
0 0 0 0 1 0
0 0 0 0 -1 0
0 0 0 0 0 1
0 0 0 0 0 -1
0 0 0 1 -1 0
0 0 0 1 0 -1
0 0 0 -1 1 0
0 0 0 0 1 -1
0 0 0 -1 0 1
0 0 0 0 -1 1
```

After saving the matrix and the contrasts in `.mat` and `.con` files, `randomise`
can be run using the usual command:

`randomise -i <skeletonized_data> -o <output_basename> -m <mean_FA_skeleton_mask> -d <design.mat> -t <design.con> -n <n_permutations> [--T2] [-V]`

as described in [TBSS user manual](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/Randomise/UserGuide).

See also:
[https://github.com/xgrg/alfa/blob/master/build_matrix.py](https://github.com/xgrg/alfa/blob/master/build_matrix.py)

You may also check this package which contains the various helper functions 
related to TBSS.
[GitHub](https://github.com/xgrg/tbss)
