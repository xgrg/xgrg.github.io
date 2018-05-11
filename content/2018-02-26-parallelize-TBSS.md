Title: How to parallelize TBSS / randomise (sort of)
Category: TBSS
Status: Published
Tags: tbss
Authors: Grégory Operto

Lots of resources - which I surely have not exhausted - are available on how
to make optimal use of TBSS and in particular of the lengthy repetitive
`randomise` part and the way to reduce costs in execution time.
I confess I may have not tried hard after my first issues with [`randomise_parallel`](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/Randomise/UserGuide#Parallelising_Randomise)
and despite being a big fan of [Nipype](http://nipype.readthedocs.io/en)
I could not find my heart's desire (if only there [would be a way](https://neurostars.org/t/fsl-randomise-parallel/268) to it).

<!-- PELICAN_END_SUMMARY -->

Nevertheless my ambition was quite humble at this point: allow `randomise` to
use `N` available CPUs to estimate a set of `M` contrasts - in parallel - using the
traditional threshold-free permutation scheme.

## TL;DR

> <div style="padding:20px; text-align:justify; background-color:#222222">
> The easiest way is probably by creating as many `.con` files as contrasts and
> to run `randomise` separately on each of them setting adecuate options to name
> the generated files in output. The workaround proposed below is nothing but a
> variation around this, with the advantage of preserving the contrast
> numbering given by `randomise` in normal conditions.</div>

See [this repository](https://github.com/xgrg/tbss/) for a proposed implementation.

## Concept:

The typical `randomise` command looks like:

```bash
`randomise -i <skeletonized_data> -o <output_basename> -m <mean_FA_skeleton_mask>\
   -d <design.mat> -t <design.con> -n <n_permutations> [--T2] [-V]`
```

This will start estimating every given contrast from the `.con` file, one after
the other, using a single processor and will generally take a substantial
amount of time, multiplied by the number of contrasts.

One dirty way to divide this time would then consist in splitting the `.con` file in
various smaller ones and to run various instances of `randomise` in parallel on them.
`randomise` names the produced statistical maps _after the rank/number of the corresponding
contrast in the `.con` file_ so it will be important that the ranks/numbers are
**consistent** between the initial file and the small bits.

For example, with `M=16` contrasts and `N=6` CPUs, we could make 6 mini-batches of
3, 3, 3, 3, 3 and 1 contrast(s) each, respectively. The first batch (call it
`part1.con`) will take the 3 first contrasts, `part2.con` the 3
following ones, etc. Now to make sure that the numbers do match between the
initial `design.con` file and the small `part*.con`, the trick consists in
adding as many *dummy contrasts* as necessary *before* the "real ones". For instance,
`part2.con` will contain 6 contrasts in total, 3 dummy contrasts + 3 genuine
ones (#4, #5, #6) from `design.con`. Then `randomise` has a hidden special `skipTo`
option to ignore the first contrasts of a file and to [start from a given one](https://www.jiscmail.ac.uk/cgi-bin/webadmin?A2=fsl;91ea4524.1402)
directly. This will be conveniently used to skip the initial *dummy contrasts*
in every `.con` file.


## Splitting the contrast file (_aka the `.con` trick_):

In short, we can adapt a function from a previous post on [building design
matrices and contrast for TBSS in Python](../building-design-matrices-for-tbss/)
to create these mock contrasts as wished.

```python
def build_tbss_contrasts(contrasts, mock=0):
    con = ['/NumWaves %s'%len(contrasts[0][1])]

    contrasts2 = []
    for i in xrange(mock):
        contrasts2.append(('mock%s'%(i+1), [0]*len(contrasts[0][1])))
    contrasts2.extend(contrasts)

    for i, (name, contrast) in enumerate(contrasts2):
        con.append('/ContrastName%s %s'%(i+1, name))
    nb_contrasts = len(contrasts2)
    con.append('/NumContrasts %s'%str(nb_contrasts))
    con.append('/Matrix')
    for i, (name, c) in enumerate(contrasts2):
        con.append(' '.join([str(each) for each in c]))

    return '\n'.join(con)
```

This function may then be wrapped in one which will split the contrasts and
generate the small files appropriately.

```python
import math

def dump(contrasts, fp):
    def chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    chunk_size = math.ceil(len(contrasts)/len(fp))
    for i, (each, f) in enumerate(zip(chunks(contrasts, chunk_size), fp)):
        w = open(f, 'w')
        w.write(build_tbss_contrasts(each, mock=i*chunk_size))
        w.close()
```

`dump` will take a list of contrasts (following the format from that [previous post](../building-design-matrices-for-tbss/))
and will dispatch them into as many files as passed in `fp`.


### Example #1: just creating mock contrasts with some design matrix:

```python
contrasts = tbss_covariates_simple_contrasts(['age', 'gender', 'apoe'])
con = build_tbss_contrasts(contrasts, mock=3)
print(con)
```

This adds 3 dummy contrasts (full of zeros) before the 6 _main effects_.

```
/NumWaves 3
/ContrastName1 mock1
/ContrastName2 mock2
/ContrastName3 mock3
/ContrastName4 age(+)
/ContrastName5 age(-)
/ContrastName6 gender(+)
/ContrastName7 gender(-)
/ContrastName8 apoe(+)
/ContrastName9 apoe(-)
/NumContrasts 9
/Matrix
0 0 0
0 0 0
0 0 0
1 0 0
-1 0 0
0 1 0
0 -1 0
0 0 1
0 0 -1
```

### Example #2: build the contrasts and split them into several files:

In this one, we have `M=6` contrasts and `N=6` processors available. The contrasts
hence can be divided into 6 "batches" of 1 contrast each.

```python
n_cpus = 6
contrasts = tbss_covariates_simple_contrasts(['age', 'gender', 'apoe'])
con = build_tbss_contrasts(contrasts)
with open('design.con', 'w') as w:
   w.write(con)

dump(contrasts, ['/tmp/part%s.con'%str(i+1) for i in xrange(n_cpus)])
```

`design.con` contains the original full list of contrasts (the file as it would
be running `randomise` the usual way). It would look like:

```
/NumWaves 3
/ContrastName1 age(+)
/ContrastName2 age(-)
/ContrastName3 gender(+)
/ContrastName4 gender(-)
/ContrastName5 apoe(+)
/ContrastName6 apoe(-)
/NumContrasts 6
/Matrix
1 0 0
-1 0 0
0 1 0
0 -1 0
0 0 1
0 0 -1
```

Each `part*.con` would then contain a single contrast from the 6 preceded by a
right number of dummy constrasts. For instance, `/tmp/part5.con` would look like:

```
/NumWaves 3
/ContrastName1 mock1
/ContrastName2 mock2
/ContrastName3 mock3
/ContrastName4 mock4
/ContrastName5 apoe(+)
/NumContrasts 5
/Matrix
0 0 0
0 0 0
0 0 0
0 0 0
0 0 1
```


## Building the proper `randomise` commands:

Now that the `M=6` contrasts are all in `N=6` files, the final part consists in
building the commands that will run `randomise` over these `N` files,
using the right `skipTo` option. Let us assume that all the `<arguments>` will be
replaced with correct paths to the actual data.

```python
import math

nb_contrasts = len(contrasts)
n_cpus = 6
chunk_size = math.ceil(nb_contrasts / n_cpus)
skipto = 1

for i in xrange(n_cpus):
    cmd = 'randomise -i <skeletonized_data> -o <output_basename> -m <mean_FA_skeleton_mask> '\
	'-d <design.mat> -t /tmp/part%s.con -n 5000 --T2 --skipTo=%s -V &> /tmp/log%s.log'\
        %(i+1, skipto, i+1)
    skipto = skipto + chunk_size
    commands.append(cmd)

for each in commands:
    print each
```

```
randomise -i <skeletonized_data> -o <output_basename> -m <mean_FA_skeleton_mask>\
   -d <design.mat> -t /tmp/part1.con -n 5000 --T2 --skipTo=1 -V &> /tmp/log1.log

randomise -i <skeletonized_data> -o <output_basename> -m <mean_FA_skeleton_mask>\
   -d <design.mat> -t /tmp/part2.con -n 5000 --T2 --skipTo=2 -V &> /tmp/log2.log

randomise -i <skeletonized_data> -o <output_basename> -m <mean_FA_skeleton_mask>\
   -d <design.mat> -t /tmp/part3.con -n 5000 --T2 --skipTo=3 -V &> /tmp/log3.log

randomise -i <skeletonized_data> -o <output_basename> -m <mean_FA_skeleton_mask>\
   -d <design.mat> -t /tmp/part4.con -n 5000 --T2 --skipTo=4 -V &> /tmp/log4.log

randomise -i <skeletonized_data> -o <output_basename> -m <mean_FA_skeleton_mask>\
   -d <design.mat> -t /tmp/part5.con -n 5000 --T2 --skipTo=5 -V &> /tmp/log5.log

randomise -i <skeletonized_data> -o <output_basename> -m <mean_FA_skeleton_mask>\
   -d <design.mat> -t /tmp/part6.con -n 5000 --T2 --skipTo=6 -V &> /tmp/log6.log
```

Eventually these lines may be saved in a script and passed to any tool like [GNU parallel](https://www.gnu.org/software/parallel/)
for execution, as in the following example:

### Example:

```bash
cat /tmp/script.sh | parallel -j <n_cpus>
```

Writing this post will have taken the actual time of running `randomise` in
background over a dataset of 500 subjects including 12 contrasts with 5000
permutations each "in parallel" following this same strategy. Much shorter
than the original _vanilla_ way.

Please comment if you have different experience or feedback to share.

