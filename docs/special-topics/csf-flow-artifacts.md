# CSF Flow Artifacts

## Overview

CSF pulsation creates motion artifacts on spine MRI that can mimic intradural pathology. These artifacts result from CSF flowing in synchrony with the cardiac cycle — systolic flow produces phase-encoding ghosts that project across the image.

## Appearance

- Smeared signal or ghost images within the thecal sac, typically in the phase-encoding direction
- Can mimic intradural masses, arachnoiditis, or filling defects
- Most prominent in the thoracic spine (where the subarachnoid space is largest relative to the cord)
- More conspicuous on T2-weighted sequences (where CSF is bright)

## How to Recognize

- The artifact repeats at regular intervals in the phase-encoding direction
- The artifact "moves" if the phase-encoding direction is changed
- Flow artifacts do not persist on post-contrast T1 images
- Cardiac-gated sequences reduce or eliminate the artifact

## Mitigation

- **Cardiac gating** — Synchronizes acquisition with the cardiac cycle
- **Flow compensation** (gradient moment nulling) — Reduces phase errors from flowing CSF
- **Spatial saturation bands** — Placed above and below the imaging volume to suppress inflowing CSF
- **Swap phase/frequency direction** — Moves the artifact away from the area of interest

!!! tip "Clinical Pearl"
    When you see a questionable intradural filling defect on T2-weighted thoracic spine MRI, consider CSF flow artifact before calling it pathology. The clue: the artifact repeats in the phase-encoding direction and is not visible on T1 post-contrast images. If uncertain, repeat with cardiac gating or swap the phase-encoding direction.

## Key Points

- CSF pulsation creates ghost images that can mimic intradural pathology
- Most common in the thoracic spine on T2 sequences
- Repeating pattern in the phase-encoding direction is the clue
- Cardiac gating and flow compensation reduce the artifact
- Always correlate with T1 post-contrast if an intradural lesion is suspected

## Related Articles

- [MRI Artifacts and Pitfalls](mri-artifacts-pitfalls.md)
- [Truncation Artifact](truncation-artifact.md)
