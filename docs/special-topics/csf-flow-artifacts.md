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

## References

1. Pai V, Boutet A, Malik M, et al. Differentiating CSF flow artifacts from pathology: an educational review. Insights Imaging. 2025;16:288. PMCID: PMC12722609. Available from: https://pmc.ncbi.nlm.nih.gov/articles/PMC12722609/
2. Quint DJ, Patel SC, Sanders WP, Hearshen DO, Boulos RS. Importance of absence of CSF pulsation artifacts in the MR detection of significant myelographic block at 1.5 T. AJNR Am J Neuroradiol. 1989;10(5):1089-1095. PMID: 2505525. Available from: https://pubmed.ncbi.nlm.nih.gov/2505525/
3. Ehman RL, Felmlee JP. Flow artifact reduction in MRI: a review of the roles of gradient moment nulling and spatial presaturation. Magn Reson Med. 1990;14(2):293-307. PMID: 2345509. Available from: https://pubmed.ncbi.nlm.nih.gov/2345509/
4. Wymer DT, Patel KP, Burke WF 3rd, Bhatia VK. Phase-Contrast MRI: Physics, Techniques, and Clinical Applications. RadioGraphics. 2020;40(1):122-140. PMID: 31917664. Available from: https://pubmed.ncbi.nlm.nih.gov/31917664/
5. CSF turbulent flow MRI artifact. Radiopaedia.org. Available from: https://radiopaedia.org/cases/mri-artifact-by-csf-turbulent-flow-1

## Related Articles

- [MRI Artifacts and Pitfalls](mri-artifacts-pitfalls.md)
- [Truncation Artifact](truncation-artifact.md)
