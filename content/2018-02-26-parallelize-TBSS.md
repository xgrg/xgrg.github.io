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
traditional threshold-free permutation scheme. Instead of losing time running
one contrast after the other.

## TL;DR

> <div style="padding:20px; text-align:justify; background-color:#222222">
> The following method is probably the dumbest way to parallelize `randomise`
> as it actually splits a `.con` file into various smaller files and returns
> a set of `randomise` commands ready to run. Instead of running all the
> contrasts sequentially one after the other, multiple jobs are used, hence
> dividing execution time while preserving the numbering of the contrasts as
> given in the original `.con` file.
 </div>

The following recipe is implemented in this [module](https://github.com/xgrg/tbss/).

## Concept:

The typical `randomise` command looks like:

```bash
`randomise -i <skeletonized_data> -o <output_basename> -m <mean_FA_skeleton_mask>\
   -d <design.mat> -t <design.con> -n <n_permutations> [--T2] [-V]`
```

This will estimate every given contrast from the `.con` file, sequentially,
 using a single processor and will generally take a substantial
amount of time, multiplied by the number of contrasts.

One dirty way to divide this time consists in splitting the `.con` file in
various smaller ones and to run various instances of `randomise` in parallel on them.
`randomise` names the produced statistical maps _after the rank/number of the corresponding
contrast in the `.con` file_ so it will be important that the ranks/numbers are
**consistent** between the initial file and the small bits.

For example, with `M=16` contrasts and `N=6` CPUs, we could make 6 mini-batches of
3, 3, 3, 3, 3 and 1 contrast(s) each, respectively. The first batch (call it
`part1.con`) will take the 3 first contrasts, `part2.con` the 3
following ones, etc. Now to make sure that the numbers do match between the
initial `design.con` file and the small `part*.con`, the trick consists in
adding as many dummy contrasts as necessary *before* the "real ones". For instance,
`part2.con` will contain 6 contrasts in total, 3 dummy contrasts + 3 genuine
ones (#4, #5, #6) from `design.con`. Then we use `randomise`'s hidden `skipTo`
option to ignore the first contrasts of a file and to [start from a given one](https://www.jiscmail.ac.uk/cgi-bin/webadmin?A2=fsl;91ea4524.1402)
directly. This will conveniently skip the initial dummy contrasts
in every `.con` file.


## Splitting the contrast file (_aka the `.con` trick_):

In short, we can adapt a function from a previous post on [building design
matrices and contrast for TBSS in Python](../building-design-matrices-for-tbss/)
to create these mock contrasts as wished. In the following example, we defined a
set of 8 contrasts over 9 independent variables.

Example:

```python
con = [('age(+)', [0, 0, 1, 0, 0, 0, 0, 0, 0]),
       ('age(-)', [0, 0, -1, 0, 0, 0, 0, 0, 0]),
       ('sex(m>f)', [0, 0, 0, 1, 0, 0, 0, 0, 0]),
       ('sex(f>m)', [0, 0, 0, -1, 0, 0, 0, 0, 0]),
       ('apoe4(+)', [0, 0, 0, 0, 0, 0, 0, 0, 1]),
       ('apoe4(-)', [0, 0, 0, 0, 0, 0, 0, 0, -1]),
       ('sleep(+)', [0, 0, 0, 0, 0, 0, 0, 1, 0]),
       ('sleep(-)', [0, 0, 0, 0, 0, 0, 0, -1, 0])]

from tbss import contrasts
contrasts.dump(con, '/tmp/contrasts.con')       
```

The contents of the generated file (following the format from that [previous post](../building-design-matrices-for-tbss/) will be the following:
```
/NumWaves 9
/ContrastName1 age(+)
/ContrastName2 age(-)
/ContrastName3 sex(m>f)
/ContrastName4 sex(f>m)
/ContrastName5 apoe4(+)
/ContrastName6 apoe4(-)
/ContrastName7 sleep(+)
/ContrastName8 sleep(-)
/NumContrasts 8
/Matrix
0 0 1 0 0 0 0 0 0
0 0 -1 0 0 0 0 0 0
0 0 0 1 0 0 0 0 0
0 0 0 -1 0 0 0 0 0
0 0 0 0 0 0 0 0 1
0 0 0 0 0 0 0 0 -1
0 0 0 0 0 0 0 1 0
0 0 0 0 0 0 0 -1 0
```

Now, let us provide a list of filepaths instead of a single one.

 ```python
 fp = ['/tmp/part1.con', '/tmp/part2.con', '/tmp/part3.con', '/tmp/part4.con']
 contrasts.dump(con, fp)  
 ```

Since we have `M=8` contrasts and `N=4` files (for, say, `N=4` processors
  available), `part*.con` would then contain two contrasts from the 8 preceded
  by the right number of dummy constrasts. For  example, the contents of the
  last one will be:

```
/NumWaves 9
/ContrastName1 mock1
/ContrastName2 mock2
/ContrastName3 mock3
/ContrastName4 mock4
/ContrastName5 mock5
/ContrastName6 mock6
/ContrastName7 sleep(+)
/ContrastName8 sleep(-)
/NumContrasts 8
/Matrix
0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 1 0
0 0 0 0 0 0 0 -1 0
```


## Building the right `randomise` commands:

Say we want the `M=8` contrasts to run on `N=4` processors. We need to build
  `N` `randomise` commands over `N` contrast files. Let us assume in the following
  that all the `<arguments>` will be replaced with correct paths to the actual
  data.
The `randomise_parallel` function takes care of all this.


```python
num_perm = 1000
n_cpus = 4
sleep_interval = 0
commands = contrasts.randomise_parallel('<skeletonized_data>',
                                        '<output_basename>',
                                        '<design.mat>',
                                        '<mean_FA_skeleton_mask>',
                                        '<contrasts.con>', num_perm=num_perm,
                                        n_cpus=n_cpus,
                                        sleep_interval=sleep_interval)
for e in commands[:]:
    print e
```

```
randomise -i <skeletonized_data> -o <output_basename> -m <mean_FA_skeleton_mask>\
   -d <design.mat> -t /tmp/part1.con -n 5000 --T2 --skipTo=1 -V &> /tmp/log1.log

randomise -i <skeletonized_data> -o <output_basename> -m <mean_FA_skeleton_mask>\
   -d <design.mat> -t /tmp/part2.con -n 5000 --T2 --skipTo=3 -V &> /tmp/log2.log

randomise -i <skeletonized_data> -o <output_basename> -m <mean_FA_skeleton_mask>\
   -d <design.mat> -t /tmp/part3.con -n 5000 --T2 --skipTo=5 -V &> /tmp/log3.log

randomise -i <skeletonized_data> -o <output_basename> -m <mean_FA_skeleton_mask>\
   -d <design.mat> -t /tmp/part4.con -n 5000 --T2 --skipTo=7 -V &> /tmp/log4.log

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
than the original way.

Please comment if you have different experience or feedback to share.
