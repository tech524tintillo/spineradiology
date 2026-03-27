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

## Related Articles

- [CSF Flow Artifacts](csf-flow-artifacts.md)
- [Truncation Artifact](truncation-artifact.md)
