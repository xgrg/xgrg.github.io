_NLM_Title: Denoising Diffusion-Weighted Imaging Data: some comparative tests
Category: Image
Status: Draft
Tags: imaging
Authors: Grégory Operto

We have been trying different software packages for the preprocessing of  diffusion-weighted imaging (DWI) and have been comparing their results in application to our cohort. We have focused on denoising in particular. This post is to give some brief feedback on our experience and give some details on the reasoning that led to our final selection.

# The history

We began several years ago with overcomplete local PCA as described in [Manjón et al., 2013](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0073021), that has been available for many years as a Matlab toolbox and gave full satisfaction. We then looked for another possible implementation that would free us from Matlab and did some tests with the [`DenoiseImage`](https://manpages.debian.org/experimental/ants/DenoiseImage.1.en.html) command provided by `ANTs`, presented as a C++ version of the original spatially adaptive non-local means (_NLM_) described in [Manjón et al., 2010](https://pubmed.ncbi.nlm.nih.gov/20027588/).
We opted for this tool using the Rician model, in accordance with the many references describing noise in DWI as being Rician.

At some point we revised the preprocessing pipeline and added [`TOPUP`](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/topup) (see [here](https://fsl.fmrib.ox.ac.uk/fslcourse/lectures/practicals/fdt1/index.html#topup) and [there](http://andysbrainblog.blogspot.com/2014/08/dti-analysis-steps-1-2-distortion.html) for tutorials) for susceptibility-induced distortion correction. Since then we started observing some issues such as voxels with negative values in mean diffusivity (MD) maps, which are normally supposed to be positive. Those negative voxels mainly appeared next to the ventricles and other areas close to cerebrospinal fluid, where diffusivity is generally the highest.

![01]({filename}images/dtifit/01.png)
![21]({filename}images/dtifit/21.png)

After some research we finally related this to a cross effect between `TOPUP` and `ANTs`' denoising using the Rician model. We switched to Gaussian model and observed that negative areas disappeared from MD maps, which would since then show a more normal profile with positive values. Instead of simply changing models and closing the issue, we took this chance to extend our investigation to some other software and potentially upgrade the pipeline with some more recent techniques.

In particular, the [Marchenko-Pastur PCA](https://cai2r.net/resources/denoising-using-marchenko-pastur-principal-component-analysis/) <a name="ref3"></a>[[3](#ref3a)] is regarded as a state-of-the-art technique that outperforms prior overcomplete local PCA. It has implementations in various modern packages such as [dipy]() or mrtrix3[], therefore plugging it into any processing workflow is not that of a big concern. We quickly realized that in comparison to our previous pipelines this new type of techniques combined good performance in removing noise and preserving of anatomical details.

# The data

Our DWI is acquired according to the following protocol:

 - 2.2 mm<sup>3</sup> isometric voxel resolution; 66 axial slices
 - FOV 230mm
 - TR = 9000ms
 - TE = 90ms
 - b-value = 1300s/m2
 - 65 directions + 8 b0 volumes

We picked around 20 different subjects and took them through the following processes:

- Denoising of DWI data by each of the selected techniques
- `TOPUP` based on the normal and reverse-encoded B0 maps
- Brain extraction of the distortion-corrected averaged b=0
image (`FSL BET`)
- Correct for eddy currents, subject motion and susceptibility-induced
distortions using topup estimates (`FSL eddy`)
- Compute QC metrics derived from TOPUP and eddy tools (`FSL eddyQC`).
- Fit diffusion tensor models and generate parametric maps (`FSL DTIFIT`)

We repeated the process in different versions using different software:

- ANTs with Rician model
- ANTs with Gaussian model
- CAT12 with Gaussian model
- [mrtrix3](https://mrtrix.readthedocs.io/en/latest/)
- [dipy](https://dipy.org/documentation/1.4.0./interfaces/denoise_flow/) ([LPCA](https://dipy.org/documentation/1.0.0./examples_built/denoise_localpca/), [MPPCA], [_NLM_](https://dipy.org/documentation/1.4.1./examples_built/denoise_nlmeans/), [Patch2Self](https://dipy.org/documentation/1.4.0./examples_built/denoise_patch2self/))
- No denoising

![02]({filename}images/dtifit/02.png)

![04]({filename}images/dtifit/04.png)

![06]({filename}images/dtifit/06.png)

![12]({filename}images/dtifit/12.png)

![15]({filename}images/dtifit/15.png)

![16]({filename}images/dtifit/16.png)

![17]({filename}images/dtifit/17.png)

![18]({filename}images/dtifit/18.png)
![19]({filename}images/dtifit/19.png)
![20]({filename}images/dtifit/20.png)


![22]({filename}images/dtifit/22.png)
![23]({filename}images/dtifit/23.png)



Concatenate both normal and reverse-encoded volumes

# The conclusion (current pipeline)

Some modern, mature, maintained and easy-to-plug implementations are now available for denoising of DWI. This includes at least software such as [`dipy`](https://dipy.org/documentation/1.4.0./interfaces/denoise_flow/)  or [`mrtrix3`](https://mrtrix.readthedocs.io/en/latest/). In application to our tests they both yielded good results based on QC metrics and visual inspection. Those were primarily designed for DWI, contrary to denoising based on NLM as done in other toolboxes (`CAT12`, `ANTs`) which are mainly oriented towards T1.

We finally selected the following pipeline and implemented a set of systematic checks for quality control, based on validators (as described in  <a name="ref4"></a>[4](#ref4a)).

<div style="padding:20px; text-align:justify; background-color:#50453e; color:white">

 <li>Denoising of the resulting volume using `mrtrix` `MPPCA`</li>
 <li>`TOPUP` based on the normal and reverse-encoded B0 maps</li>
 <li>Brain extraction of the distortion-corrected averaged b=0 image (`FSL BET`)</li>
 <li>Correct for eddy currents, subject motion and susceptibility-induced distortions using topup estimates (`FSL eddy`)</li>
 <li>Compute QC metrics derived from TOPUP and eddy tools (`FSL eddyQC`).</li>
 <li>Fit diffusion tensor models and generate parametric maps (`FSL DTIFIT`)</li>
 <li>Compute radial diffusivity map (using `FSL fslmaths`)</li>

</div>

Steps for automatic QC (bbrc-validator):
<div style="padding:20px; text-align:justify; background-color:#50453e; color:white">

<li>Count negative voxels and check that they are under a certain limit.</li>
<li>Measure SNR/CNR using eddyqc and check that they are within a certain range</li>

</div>

Huge kudos and most credits to Jordi Huguet who took all the burden of running these tests with those different techniques, extracting metrics for comparison and analyzing them. All the figures in this post are attributed to his work.

### References

1.[↑](#ref1) <a name="ref1a"></a>
 _J. Manjón, P. Coupé, L. Concha, A. Buades, L. Collins, M. Robles,_  [Diffusion Weighted Image Denoising Using Overcomplete Local PCA](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0073021), PLOS One (2013)

 2.[↑](#ref2) <a name="ref2a"></a> _P. Coupe, J. Manjon, M. Robles, L. Collins_, [Adaptive Multiresolution Non-Local Means Filter for 3D MR Image Denoising](https://hal.archives-ouvertes.fr/hal-00645538/document), IET Image Processing, Institution of Engineering and Technology (2011)

 3.[↑](#ref3) <a name="ref3a"></a> _J. Veraart J, DS. Novikov, D. Christiaens, B. Ades-Aron, J. Sijbers, E. Fieremans_,
[Denoising of diffusion MRI using random matrix theory](https://www.sciencedirect.com/science/article/abs/pii/S1053811916303949)
Neuroimage (2016)

 4.[↑](#ref4) <a name="ref4a"></a> _J. Huguet, C. Falcon, D. Fusté, S. Girona, D. Vicente, JL Molinuevo, JD Gispert, G. Operto for the ALFA Study_,
[Management and Quality Control of Large Neuroimaging Datasets: Developments From the Barcelonaβeta Brain Research Center](https://www.frontiersin.org/articles/10.3389/fnins.2021.633438/full), Front. in Neurosc. (2021)
