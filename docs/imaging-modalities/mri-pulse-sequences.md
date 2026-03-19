# MRI Pulse Sequences for Spine

## Definition

MRI pulse sequences are specific combinations of radiofrequency pulses and magnetic field gradients that determine the contrast characteristics of the resulting images. Different sequences highlight different tissue properties, and selecting the appropriate sequences is essential for accurate spine evaluation.

## Core Sequences

### T1-Weighted Imaging

- **Contrast mechanism:** reflects differences in T1 relaxation times; tissues with short T1 (fat, gadolinium, methemoglobin) appear bright
- **Key features:** excellent anatomic detail; fat is bright; CSF is dark; marrow is bright (adult fatty marrow)
- **Spine applications:** marrow evaluation, foraminal anatomy (bright epidural fat outlines dark nerve roots), post-contrast enhancement detection

### T2-Weighted Imaging

- **Contrast mechanism:** reflects differences in T2 relaxation times; tissues with long T2 (water, CSF) appear bright
- **Key features:** CSF is bright ("myelographic effect"); fluid/edema is bright; normal cord is intermediate
- **Spine applications:** disc evaluation (hydration = bright, desiccation = dark), stenosis assessment, cord signal abnormalities, detection of edema and fluid collections

### STIR (Short Tau Inversion Recovery)

- **Contrast mechanism:** an inversion recovery sequence that selectively suppresses fat signal while highlighting water/edema
- **Key features:** fat is dark (suppressed); edema and fluid are very bright; extremely sensitive to pathology
- **Spine applications:** bone marrow edema (acute fractures, metastases, infection), ligamentous injury, inflammatory disease

### Proton Density (PD)

- **Contrast mechanism:** reflects the number of mobile hydrogen protons per unit tissue
- **Key features:** intermediate contrast between T1 and T2; not commonly used in spine MRI as a primary sequence
- **Spine applications:** occasionally used for disc evaluation and cartilage assessment

## Advanced Sequences

### Gradient Echo (GRE)

- Fast acquisition with T2*-weighted contrast
- Sensitive to magnetic susceptibility effects (blood products, calcification, metallic artifact)
- Used for detecting hemorrhage in the cord and evaluating cord compression in cervical spondylotic myelopathy
- Blooming artifact near metallic hardware limits use in post-surgical patients

### Diffusion-Weighted Imaging (DWI)

- Measures the random motion of water molecules (Brownian motion)
- Restricted diffusion (bright on DWI, dark on ADC map) indicates dense cellularity or cytotoxic edema
- Spine applications: differentiating acute vertebral compression fracture (restricted) from chronic fracture (no restriction); abscess detection; tumor characterization

### Fat-Saturated Sequences

- **Chemical fat saturation:** applies a frequency-selective pulse to suppress fat signal; used with T2 and post-contrast T1
- **Dixon technique:** separates water and fat signals mathematically; more uniform fat suppression than chemical saturation
- Used to confirm that bright T1 signal is due to fat (signal drops with fat sat) vs. other causes (blood, protein)

### T2* (T2-Star)

- A gradient echo-based sequence sensitive to magnetic field inhomogeneities
- Useful for detecting hemorrhage, calcification, and metallic fragments
- Can help identify intramedullary hemorrhage in acute spinal cord injury

## Sequence Selection by Clinical Scenario

| Clinical Question | Essential Sequences |
|-------------------|-------------------|
| **Disc herniation** | Sagittal T2, Axial T2, Sagittal T1 |
| **Spinal stenosis** | Sagittal T2, Axial T2, Sagittal T1 |
| **Acute fracture** | Sagittal STIR (edema detection), Sagittal T1 (fracture line) |
| **Metastatic disease** | Sagittal STIR, Sagittal T1, Post-contrast T1 fat-sat |
| **Infection** | Sagittal STIR, Sagittal T1, Post-contrast T1 fat-sat (essential) |
| **Post-surgical** | Post-contrast T1 fat-sat (scar enhances, recurrent herniation does not) |
| **Cord lesion** | Sagittal T2, Sagittal T1, Post-contrast T1, DWI |
| **Trauma (ligaments)** | Sagittal STIR, Sagittal T2 |

!!! tip "Clinical Pearl"
    The key to distinguishing **recurrent disc herniation from post-surgical scar tissue** is gadolinium-enhanced T1 with fat saturation. Scar tissue enhances uniformly and early (within 5 minutes), while recurrent disc herniation does not enhance centrally (only peripheral enhancement may be seen). This distinction is critical because scar tissue is typically not surgically treated, while symptomatic recurrent herniation may require reoperation.

## Key Points

- T1 shows anatomy (fat bright, CSF dark); T2 shows pathology (fluid bright, CSF bright)
- STIR is the most sensitive sequence for edema and is essential for acute fractures, infection, and inflammation
- DWI helps differentiate acute from chronic compression fractures
- Post-contrast T1 with fat saturation is essential for tumor, infection, and post-surgical evaluation
- Sequence selection should be tailored to the clinical question
- Sagittal T2 is the single most important screening sequence for spine MRI

## Related Articles

- [MRI of the Spine](mri-spine.md)
- [Gadolinium Enhancement](gadolinium-enhancement.md)
- [Diffusion-Weighted Imaging (DWI) of the Spine](dwi-spine.md)
- [Spinal Cord](../anatomy/spinal-cord.md)
