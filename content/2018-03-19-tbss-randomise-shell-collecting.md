Title: TBSS/Randomise shell collecting
Category: TBSS
Status: Draft
Tags: tbss
Authors: Grégory Operto

=============================================

2013/2/8 Ksenia Andreyeva <[log in to unmask]>
Dear Sir/Madam,

I have a few technical quires about the FSL Randomise algorithm. I am a mathematician by training and although statistics is not my main area of expertise, I know the basics fairly well. I have read the user manual on your website and I have studied the FSL statistics summer course notes and I gained some understanding on how Randomise should be used, but some things are still not clear to me and I would really appreciate it if you could clarify them for me.

1) Which distribution-free equivalents of parametric tests are actually available? I apologize for asking such a primitive question, but even after reading the manual pages this remained unclear to me. This is how I understand it: Randomise recognizes the design matrices that correspond to 2-sample unpaired t-tests with and without nuisance variables, 2-sample paired t-test and repeated values ANOVA. All the rest of the design matrices are recognized as not fitting the criteria for the above tests and are treated in the same way by fitting a linear regression model to the supplied data and then performing individual t-tests to identify the factors with coefficients significantly different from zero. Could you confirm that this is correct?


Actually, the question is somewhat ill-posed... The t-tests (paired, unpaired, with or without nuisance), F-tests (ANOVA, ANCOVA), and simple and multiple linear regression, all of them can be formulated as the same linear model (aka, the "general linear model"). The parameters of this model can then be used for hypothesis testing. Although we may think of these tests as being distinct entities, often carried out using entirely different procedures and equations (indeed, many classical books present the material in this way), they are all variants of the more general formulation given by the GLM.

So, about "Which distribution-free equivalents of parametric tests are actually available?", the answer is virtually any test that can be accommodated within the GLM. Perhaps the only exception is the repeated measures designs, but even these, in some particular cases and with some reasonable assumptions, can be performed too. Note, however, that the statistics available (not to be confused with the tests themselves) are t, F, and TFCE. R^2 is not available directly.


 Also, the output of Randomise are the TFCE corrected p-values for all contrasts specified in the contrast matrix. What is not clear to me is how to obtain the goodness of fit statistic (R-squared test perhaps) which would tell me whether it would be acceptable to use the corresponding t-test results.

 To obtain the absolute value of the R^2 for an arbitrary model, divide the variance of the residuals by the variance of the data. Subtract this quotient from 1. That's all.


  2) The next question I have is whether Randomise distinguishes between categorical, ordinal and continuous data. If so, I would like to find out how to construct the design matrices in such a way that a column with values {1,2,3} would be interpreted and treated as {'drinks tea', 'drinks coffee', 'does not drink caffeinated drinks'} rather than {'small', 'medium', 'large'}. The type of data is very important for the choice of statistical test and it would be useful if I got a confirmation that ordinal data is not treated as categorical, and discrete is not treated as ordinal. It would be great if you could give me a set of instructions on how this should be reflected in the design matrix.


  There is no distinction or whatsoever between categorical, ordinal or continuous variables, nor should it be. You model however you want in the design matrix. It is indeed possible to put strict linear effects for categorical variables in columns in the design, but perhaps you could gain in flexibility by testing whether the effects follow the pattern of your hypothesis (e.g., if the 'small', 'medium' and 'large' are really in this order, and whether medium is the exact half-way through), with contrasts.


  For example, I have the following data set: TBSS skeletons for patients with motor neuron disease (MND) and healthy controls. I also have data for the MND patients on where the disease started: hands, feet or bulbar. Suppose I have 6 patients with MND (2 with each possible disease initiation type) and 2 controls. Here are the possible ways to code this data set into a design matrix:

  1 0 1
  1 0 1
  1 0 2
  1 0 2
  1 0 3
  1 0 3
  0 1 0
  0 1 0

  where the first and second columns indicate whether the participant has MND (1,0) or is a healthy control (0,1), the layout also suggests that the data is ordinal and all participants' data is exchangeable for permutation reasons; this question is addressed in the next bullet point. The third column indicates the disease initiation site: 1-hands, 2-legs, 3- bulbar, 0-data unavailable since healthy controls do not have MND. The question is does the zero indicate missing data or will it be treated as a group type? If it is, this invalidates the model.

  Another way to code the data is to specify that the MND and control groups are not exchangeable for permutation reasons and all permutations should be done within a group:

  1 1
  1 1
  1 2
  1 2
  1 3
  1 3
  2 0
  2 0

  where 1 stands for MND and 2 stands for control.

  Alternatively we could code the "MND vs controls" variable as categorical: 'a'-MND patient, 'b'-control. Once again it would be useful if you could confirm that I understand the encoding correctly!

  a 1
  a 1
  a 2
  a 2
  a 3
  a 3
  b 0
  b 0

  The data could also be coded as described in "Two-Sample Paired T-test (Paired Two-Group Difference)" section of the user manual, i.e. treating each possible value of disease initiation site as a separate variable:

  a 1 0 0
  a 1 0 0
  a 0 1 0
  a 0 1 0
  a 0 0 1
  a 0 0 1
  b 0 0 0
  b 0 0 0

  with this layout we no longer have the problem of falsely coding for disease initiation site for healthy controls. However, please correct me if I am wrong, we now have the problem of interdependency of the factors. Multi-linear regression analysis is only available for data with correlations, but not for data that has a strict dependency on each other (e.g, the probability of disease initiation in legs is zero if it initiated in hands). Could you please confirm that Randomise is not treating the last 3 columns as separate variables and is somehow combining them into one when it performs the statistical analysis?

  Needless to say, when I tried all of these methods I got very different results.


  Perhaps it might be easier if you state your hypothesis first. Would you like to check whether patients with MND differ from controls regardless of the topological site, or would you like to compare if patients with different topological lesions differ from each other? Would you like to check if there is a strictly linear increase/decrease on FA across these patient categories? If so, which in your hypothesis should have the smallest FA? Or the largest? Think about the hypothesis first, then try to assemble the design together with the contrasts.

  About the dependency, I don't see this as a problem. Likewise, the probability that someone is a control is zero given that the disease has started and the diagnosis has been made.


   3) From the way Randomise is set up it follows that the voxels of TBSS skeletons are treated as response variables, while the columns of the design matrix are the explanatory variables. For a regression model with only 1 explanatory variable the statistical significance would be the same if the response and explanatory variables were swapped. However, the same is not true for multi-linear models with several explanatory variables. Now if I wanted to test whether changes in brain structure affected cognitive ability, I would want to define FA in a voxel as a predictor variable and cognitive scores as multiple responses. For that I would like to perform a MANOVA test. Do I understand correctly that this option is not available in FSL? If I am wrong, would it be ok to give some more information on where I could find information on this test?


   The explanatory variables in the GLM are not assumed to be causing or affecting the observed variables. This is the old fallacy that correlation would imply causality. Not at all. Actually, you can still do the test you want, and interpret them as the association between brain structural changes and a cognitive score, provided that other scores and other nuisances have been taken into account in the matrix.


   4) I am currently working with a large data set of 639 normal ageing subjects and am using Randomise to analyze the TBSS data and it's association with cognitive test scores. My first target was to analyze the associations of white matter integrity and a range of cognitive tests individually. The way I constructed my design matrices was as follows: I included only one column containing the scores from a cognitive test and ran Randomise (without demeaning), and obtained no significant voxels. A colleague then suggested that I include a vector of ones in front of the cognitive scores in the design matrix. We both thought that it would not make any difference, but surprisingly (to us) it did and I then got a number of significant voxels. However, I cannot find anywhere what the column of ones actually does and whether it makes the statistical test more or less valid for my purposes. I will be extremely grateful if you could provide me with some guidelines on the significance of this column and the nature of the cases when it needs to be included.


   The linear model is simply y=ax+b or, for clarity, y=a*x + b*1. Then you see why the 1 is needed. It's the intercept.


    5) Is demeaning the data equivalent to adding a column of ones in the design matrix?

    Yes in general. However, this doesn't mean that it should always be done. Have a look at some recent posts where mean centering has been discussed to exhaustion.


     6) The user manual indicates that the data needs to be demeaned whenever we are not testing for the design matrix mean. Does this apply to categorical and ordinal data? What happens if one demeanes a design matrix that contains both categorical/ordinal and continuous data, does it subtract the mean of each column from the corresponding values, thus potentially making ordinal data continuous (e.g. {1,1,1,2,2} becoming {-0.4 ,-0.4 ,-0.4 , 0.6 , 0.6)?


     Again, there is no difference between categorical and continuous data. The difference between them is the interpretation we give to them, not on the numbers.

     All the best,

     Anderson


=================================

https://web.stanford.edu/group/vista/cgi-bin/wiki/index.php/MrVista_TBSS

Running randomise
randomise -i all_FA_skeletonised.nii.gz -o faMath -d design.mat -t design.con -n 1000 --T2 -D
The flags are

-D flag demeans the FA values.
--T2 flag sets Threshold-Free Cluster Enhancement with 2D optimisation (e.g. for TBSS data); H=2, E=1, C=26
These are the recommended flags for the randomise, version 2.5, build 414 and TBSS distributed in August, 2009. Demeaning is clear. The -T2 flag asks randomise to use the TFCE method to account for cluster sizes. TFCE adjusts the statistic in each voxel to reflect the "area of support", i.e. the values of the voxels around it, then runs the stats on the adjusted values. See Smith & Nichols (2009) NeuroImage.

The process took over an hour on green for JMT, 1000 permutations.

There are three classes of output files per contrast type.

faMath_tstat(N).nii.gz
faMath_tfce_p_tstat (and possibly faMath_tfce_p_fstat)
faMath_tfce_corrp_tstat (and possibly faMath_tfce_corrp_fstat)
We don't have the fstat files in this example.

[edit] More randomise tips
See this intuitive description of how randomise works with TFCE cluster correction (TFCE is recommended by tbss).

See the FSL FEAT page on how to set up a design matrix for a 2-sample unpaired t-test using the GLM gui.

JMT found the following threads in the FSL archives useful in setting up randomise analyses for correlations and two-sample t-tests:

For a one-sample correlation analysis: "demean" your covariates manually, and demean the brain data by using the -D option:
For a two-sample t-test, "demean" your covariates manually. If you construct your design matrix such that all the columns sum to 0, you should demean your brain data using the -D option. If one or more of your columns does not sum to zero, then likely you are modeling the mean in your design matrix already, and you do not need to use the -D option.
A reminder about how to include covariates in your design matrix.

===================================

First of all, an unpermuted t-map is computed. This would be a multiple linear regression at each voxel. TFCE is then fed with this unpermuted t-map, and an unpermuted TFCE-map is computed.

Then, at each permutation in randomise:
1. A t-map is computed (and maximum t value is stored for later generating the max(t) null distribution).
2. TFCE algorithm is fed with that t-map, TFCE-map is computed (and the maximum TFCE score is stored for later generating the null distribution).

After N permutations, we can compare our unpermuted TFCE-map with the null distribution made of N max(TFCE) scores to get a FWE-corrected p-map.
(And, if we compared the unpermuted t-map with the max(t) null distribution, we would get voxelwise FWE p-map?)

====================================

Dear Yi-Shin,

The -D option alters the data by de-meaning it; you only need this step when you have a design matrix that *does* *not* model a mean. One way to check whether a design matrix models the mean is whether each column sums to zero; if all columns sums to zero, the model cannot model any overall mean effect.

Your design matrix models the mean (in the first two columns) and hence does not require you to use the -D option.

-Tom


On Thu, Sep 11, 2008 at 3:03 PM, Yi-Shin Sheu <[log in to unmask]> wrote:
Dear FSL experts,

I searched the FSL archive but it is still kind of confusing to me about the
demean option.

I have two groups (control vs patient) and I would like to see the difference
between their FA value in TBSS analysis while controlling for the nuisance
covarietes (age).

Could anyone tell me if my design matrix is correct and if I need to add -D
option in randomise.

deisgn matrix:

EV1  EV2  EV3  EV4
1    0     -2     0
1    0     -2     0
1    0      4     0
0    1      0    -1
0    1      0     2
0    1      0    -1

EV3 is the demeaned age for control group which I padded with zeros.  EV4 is
hte demeaned age for patient group, which I also padded with zeros.

design contrast:

1 -1 (Control >Patient)
-1 1 (patient > control)

Then I run: randomise -i all_FA_skeleton -o tbss -m mean_FA_skeleton_mask -
d design.mat -t design.con -n 5000 -c 3 -D

My question is, do I have to run randomise with the -D option in this case?

I appreciate any input you might have.  Thank you so much.

   Yi-Shin
