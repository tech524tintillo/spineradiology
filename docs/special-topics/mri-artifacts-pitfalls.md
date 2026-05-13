# MRI Artifacts and Pitfalls

## Overview

Spine MRI is susceptible to several artifacts that can mimic pathology or obscure true findings. Recognizing these artifacts is essential for accurate interpretation.

## Common Artifacts

### Motion Artifact
- Ghosting in the phase-encoding direction from patient breathing, swallowing, or CSF pulsation
- Appears as repeated images of high-signal structures (e.g., aorta, CSF) smeared across the image
- Mitigation: motion-compensating sequences, saturation bands, shorter acquisition times

### Susceptibility Artifact
- Signal loss and geometric distortion at interfaces between tissues with different magnetic susceptibility (air-bone, metal-tissue)
- Most prominent on GRE sequences; less on FSE
- Relevant at: surgical hardware, vertebral endplates, cervicothoracic junction (lung apex)
- Mitigation: FSE sequences, increased bandwidth, MARS protocols for hardware

### Chemical Shift Artifact
- Misregistration of fat and water signals at fat-water interfaces (vertebral endplates)
- Appears as a bright or dark line at the endplate margin in the frequency-encoding direction
- Can mimic endplate fracture or Modic changes
- Mitigation: increase bandwidth, fat suppression

### Wrap-Around (Aliasing)
- Anatomy outside the field of view wraps into the image on the opposite side
- Mitigation: increase FOV, phase oversampling, swap phase/frequency directions

!!! tip "Clinical Pearl"
    **Susceptibility artifact** from surgical hardware is the biggest challenge in post-operative spine MRI. Titanium produces less artifact than stainless steel. MARS techniques (FSE instead of GRE, increased bandwidth, STIR instead of chemical fat-sat, smaller voxels) significantly improve image quality around hardware.

## Key Points

- Motion, susceptibility, chemical shift, and truncation are the most common spine MRI artifacts
- Susceptibility artifact is worst on GRE, least on FSE
- MARS techniques reduce hardware artifact
- Chemical shift at endplates can mimic fracture or Modic changes
- CSF flow artifact is covered separately

## References

1. Taber KH, Herrick RC, Weathers SW, Kumar AJ, Schomer DF, Hayman LA. Pitfalls and artifacts encountered in clinical MR imaging of the spine. RadioGraphics. 1998;18(6):1499-1521.
2. Noda C, Ambale Venkatesh B, Wagner JD, Kato Y, Ortman JM, Lima JAC. Primer on commonly occurring MRI artifacts and how to overcome them. RadioGraphics. 2022;42(3):E102-E103.
3. Olsen RV, Munk PL, Lee MJ, Janzen DL, MacKay AL, Xiang QS, Masri B. Metal artifact reduction sequence: early clinical applications. RadioGraphics. 2000;20(3):699-712.
4. Krupa K, Bekiesińska-Figatowska M. Artifacts in magnetic resonance imaging. Pol J Radiol. 2015;80:93-106.
5. MRI artifacts. Radiopaedia.org. Available from: https://radiopaedia.org/articles/mri-artifacts-1

## Related Articles

- [CSF Flow Artifacts](csf-flow-artifacts.md)
- [Truncation Artifact](truncation-artifact.md)
