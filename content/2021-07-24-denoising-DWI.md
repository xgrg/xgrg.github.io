Title: Denoising Diffusion-Weighted Imaging Data: some comparative tests
Category: Image
Status: Published
Tags: imaging
Authors: Grégory Operto

We have been trying different software packages for the preprocessing of  diffusion-weighted imaging (DWI) and comparing their results in application to our cohort data, with a particular focus set on denoising. This post gives some brief feedback on our experience and details somewhat the reasoning that led to our final selection. Those comparative tests never intended to be a systematic analysis therefore this will unlikely make it to a full paper but hopefully that might interest anyone with related methodological questions. This is also an illustration of how we manage upgrades in processing pipelines &mdash; for instance when some issue gets detected &mdash; and how we adapt our <a href="#ref4">procedures for QC</a> accordingly.

# The history

We began several years ago with the overcomplete local PCA as described in <a name="ref1"></a>[[1](#ref1a)], that has been available for many years as a Matlab toolbox and gave full satisfaction. We then looked for another possible implementation that would free us from Matlab and did some tests with the [`DenoiseImage`](https://manpages.debian.org/experimental/ants/DenoiseImage.1.en.html) command provided by `ANTs`, presented as a C++ version of the original spatially adaptive non-local means (_NLM_) described in <a name="ref2"></a>[[2](#ref2a)].
We opted for this tool using the Rician model, in accordance with the many references describing noise in DWI as being Rician.

At some point we revised the preprocessing pipeline and added [`TOPUP`](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/topup) (see [here](https://fsl.fmrib.ox.ac.uk/fslcourse/lectures/practicals/fdt1/index.html#topup) and [there](http://andysbrainblog.blogspot.com/2014/08/dti-analysis-steps-1-2-distortion.html) for some help with it) for susceptibility-induced distortion correction. Since then we started observing some issues such as voxels with negative values in mean diffusivity (MD) maps, which are normally supposed to be positive. Those negative voxels mainly appeared next to the ventricles and other areas close to cerebrospinal fluid, where diffusivity is generally the highest.

![01]({filename}images/dtifit/01.png)
![21]({filename}images/dtifit/21.png)
<center><small> The same DWI volume was applied denoising with `ANTs` using Gaussian and Rician model - then the resulting MD map (Rician version) shows a significant amount (visible in the histogram) of voxels with negative values</small></center>

After some research we finally related this to a cross effect between `TOPUP` and `ANTs`' denoising using the Rician model. We switched to Gaussian model and observed that negative areas disappeared from MD maps, which would since then show a more normal profile with positive values. Instead of simply changing models and closing the issue, we took this chance to extend our investigation to some other software and potentially upgrade the pipeline with some more recent techniques.

In particular, the [Marchenko-Pastur PCA](https://cai2r.net/resources/denoising-using-marchenko-pastur-principal-component-analysis/) <a name="ref3"></a>[[3](#ref3a)] is regarded as a state-of-the-art technique that outperforms prior overcomplete local PCA. It has implementations in various modern packages such as [`dipy`](https://dipy.org/documentation/1.4.0./interfaces/denoise_flow/) or [`mrtrix3`](https://mrtrix.readthedocs.io/en/latest), therefore plugging it into any processing workflow is not that of a big concern. We quickly realized that in comparison to our previous pipelines this new type of techniques combined good performance in removing noise and preserving of anatomical details.

# The data

Our DWI is acquired according to the following protocol:

 - 2.2 mm<sup>3</sup> isometric voxel resolution; 66 axial slices
 - FOV 230mm
 - TR = 9000ms
 - TE = 90ms
 - b-value = 1300s/m2
 - 65 directions + 8 b0 volumes

We picked ~20 random subjects and took them through the following processes:

- Denoising of DWI data by each technique in a selected set
- `TOPUP` based on normal and reverse-encoded B0 maps
- Brain extraction of the distortion-corrected averaged b=0
image (`FSL BET`)
- Correction for eddy currents, subject motion and susceptibility-induced
distortions using topup estimates (`FSL eddy`)
- QC metric estimation derived from `TOPUP` and `eddy` tools (`FSL eddyQC`).
- Model fitting and creation of parametric maps (`FSL DTIFIT`)

We repeated the process in different versions using different software:

- [`ANTs`](https://manpages.debian.org/experimental/ants/DenoiseImage.1.en.html) with Rician model
- [`ANTs`](https://manpages.debian.org/experimental/ants/DenoiseImage.1.en.html) with Gaussian model
- [`CAT12`](http://www.neuro.uni-jena.de/cat/) with Gaussian model
- [`mrtrix3`](https://mrtrix.readthedocs.io/en/latest/)
- [`dipy`](https://dipy.org/documentation/1.4.0./interfaces/denoise_flow/) ([_LPCA_](https://dipy.org/documentation/1.0.0./examples_built/denoise_localpca/), [_MPPCA_](https://dipy.org/documentation/1.0.0./examples_built/denoise_mppca/), [_NLM_](https://dipy.org/documentation/1.4.1./examples_built/denoise_nlmeans/), [_Patch2Self_](https://dipy.org/documentation/1.4.0./examples_built/denoise_patch2self/))
- No denoising

A note on denoising the reverse-encoded B0 map before `TOPUP`: as the reverse-encoded B0 map is in our case acquired as a single 3D volume, we considered two options, either 1. concatenate both normal and reverse-encoded volumes and denoise them both as a single 4D volume, or 2. do not denoise the reverse-encoded B0 map and feed it as it is into `TOPUP` with the normal-encoded B0 map, which gets denoised along with the rest of the 65 volumes. We did not consider the third option applying `TOPUP` using two *non-denoised* B0 maps.
In case 1, all volumes go under the same processing protocol but the reverse-encoded B0 map gets denoised based on an estimation made on a "different" volume; and in case 2, that B0 map is not applied any denoising at all. We tested those two approaches with one single software; in this respect some figures show references to `MRTRIX3_V1` and `MRTRIX3_V2`. In the end, we only kept the first one (concatenated volumes and denoised all at once).


# The results

A general observation is that NLM is good at removing noise but also yields noticeably smoother resulting images. In comparison MPPCA preserves anatomical details although some noise is still visible.

![04]({filename}images/dtifit/04.png)

![16]({filename}images/dtifit/16.png)


Looking at residual maps confirms that observation as less anatomical traits can be identified using MPPCA (on the right).

![18]({filename}images/dtifit/18.png)


Same observations with FA maps and RGB tensors obtained from NLM-denoised data which looked quite smoother than using MPPCA denoising.

![19]({filename}images/dtifit/19.png)

![02]({filename}images/dtifit/02.png)

![06]({filename}images/dtifit/06.png)

One big concern of ours was to make sure resulting MD maps would not include large areas with negative voxels. In that respect, NLM with Gaussian model (orange) systematically gave the lowest number of negative voxels and the minimum value closest to zero, compared to NLM with Rician model (blue) and MPPCA (green).

![12]({filename}images/dtifit/12.png)

In the end NLM with Rician model (orange) was the only method yielding so many negative voxels in MD.

![15]({filename}images/dtifit/15.png)

More techniques: same observation.

![22]({filename}images/dtifit/22.png)

We also made sure that those large initial periventricular negative areas disappeared from the final MD maps.

![20]({filename}images/dtifit/20.png)

Signal-to-noise/carrier-to-noise ratios (SNR/CNR) is also found higher using MPPCA (or CAT12) than using NLM with ANTs Rician and Gaussian (blue and orange respectively).

![17]({filename}images/dtifit/17.png)

Finally we looked at the estimation of outlier slices in each processed volume as provided by [`eddyQC`](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/eddyqc/UsersGuide) and realized that using anything but NLM-Rician improves that QC metric. To some extent NLM-Gaussian could be considered a winner in this test but it might be thought as a logical consequence of the smoother aspect of the resulting images. Less outliers but less anatomical details as well.

![23]({filename}images/dtifit/23.png)


# The conclusion (current pipeline)

Some modern, mature, maintained and easy-to-plug implementations are now available for denoising of DWI. This includes at least packages such as [`dipy`](https://dipy.org/documentation/1.4.0./interfaces/denoise_flow/)  or [`mrtrix3`](https://mrtrix.readthedocs.io/en/latest/). In application to our tests they both yielded good results based on QC metrics and visual inspection. Those were primarily designed for DWI, contrary to denoising based on NLM as done in other toolboxes (`CAT12`, `ANTs`) which are mainly oriented towards T1.

We finally selected the following pipeline and implemented a set of systematic checks for quality control, based on validators (as described in  <a name="ref4"></a>[4](#ref4a)).

<div style="padding:20px; text-align:justify; background-color:#50453e; color:white">

 <li>Denoising of the resulting volume using <code>mrtrix</code> <i>MPPCA</i></li>
 <li><code>TOPUP</code> based on the normal and reverse-encoded B0 maps</li>
 <li>Brain extraction of the distortion-corrected averaged b=0 image (<code>FSL BET</code>)</li>
 <li>Correct for eddy currents, subject motion and susceptibility-induced distortions using topup estimates (<a href="https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/eddy"><code>FSL eddy</code></a>)</li>
 <li>Compute QC metrics derived from <code>TOPUP</code> and <code>eddy</code> tools (<a href="https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/eddyqc/UsersGuide"><code>FSL eddyQC</code></a>)).</li>
 <li>Fit diffusion tensor models and generate parametric maps (<code>FSL DTIFIT</code>)</li>
 <li>Compute radial diffusivity map (using <code>FSL fslmaths</code>)</li>

</div>

Steps for automatic QC ([`bbrc-validator`](https://gitlab.com/bbrc/xnat/bbrc-validator)):
<div style="padding:20px; text-align:justify; background-color:#50453e; color:white">

<li>Count negative voxels and check that they are under a certain limit.
<a href="https://gitlab.com/bbrc/xnat/bbrc-validator/-/blob/master/bbrc/validation/processing/dtifit.py#L354"><code>DTIFITValidator.HasFewNegativeVoxelsInMD</code></a></li>
<li>Measure SNR/CNR using <a href="https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/eddyqc/UsersGuide"><code>eddyqc</code></a> and check that they are within a certain range <a href="https://gitlab.com/bbrc/xnat/bbrc-validator/-/blob/master/bbrc/validation/processing/dtifit.py#L405"><code>DTIFITValidator.HasAcceptableAverageSNR</code></a> <a href="https://gitlab.com/bbrc/xnat/bbrc-validator/-/blob/master/bbrc/validation/processing/dtifit.py#L438"><code>DTIFITValidator.HasAcceptableAverageCNR</code></a></li>
<li>Check that the total percentage of outlier slices in the volume (as detected by <code>eddy</code>) is under 1% <a href="https://gitlab.com/bbrc/xnat/bbrc-validator/-/blob/master/bbrc/validation/processing/dtifit.py#L461"><code>DTIFITValidator.HasAcceptableOutliersPercentage</code></a></li>

</div>

These checks will systematically be performed on any new execution of the DWI processing pipeline. Resulting validators now include the following additional entries, to prevent from any future regression.

![03]({filename}images/dtifit/03.png)
<center><small>
(obtained using the command <code><a href="https://gitlab.com/xgrg/bx">bx</a> dtifit report [RESOURCE_ID]</code>)</small></center>



Huge kudos and most credits to Jordi Huguet ([Barcelonaβeta Brain Research Center](http://barcelonabeta.org)) who took all the burden of running these tests with those different techniques, extracting metrics for comparison and analyzing them. All the figures in this post are attributed to his work.

### References

1.[↑](#ref1) <a name="ref1a"></a>
 _J. Manjón, P. Coupé, L. Concha, A. Buades, L. Collins, M. Robles,_  [Diffusion Weighted Image Denoising Using Overcomplete Local PCA](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0073021), PLOS One (2013)

 2.[↑](#ref2) <a name="ref2a"></a> _P. Coupé, J. Manjón, M. Robles, L. Collins_, [Adaptive Multiresolution Non-Local Means Filter for 3D MR Image Denoising](https://hal.archives-ouvertes.fr/hal-00645538/document), IET Image Processing, Institution of Engineering and Technology (2011)

 3.[↑](#ref3) <a name="ref3a"></a> _J. Veraart J, DS. Novikov, D. Christiaens, B. Ades-Aron, J. Sijbers, E. Fieremans_,
[Denoising of diffusion MRI using random matrix theory](https://www.sciencedirect.com/science/article/abs/pii/S1053811916303949)
Neuroimage (2016)

 4.[↑](#ref4) <a name="ref4a"></a> _J. Huguet, C. Falcon, D. Fusté, S. Girona, D. Vicente, JL Molinuevo, JD Gispert, G. Operto for the ALFA Study_,
[Management and Quality Control of Large Neuroimaging Datasets: Developments From the Barcelonaβeta Brain Research Center](https://www.frontiersin.org/articles/10.3389/fnins.2021.633438/full), Front. in Neurosc. (2021)
