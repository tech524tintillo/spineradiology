# Diffusion-Weighted Imaging (DWI) of the Spine

## Definition

Diffusion-weighted imaging (DWI) is an MRI technique that measures the random (Brownian) motion of water molecules within tissues. In the spine, DWI helps differentiate pathologic processes based on the degree to which water diffusion is restricted, providing functional information beyond standard anatomic sequences.

## Technique

### Physics

- DWI applies paired magnetic field gradients that sensitize the MR signal to water molecule motion
- Stationary water molecules (restricted diffusion) retain signal and appear **bright on DWI**
- Mobile water molecules (free diffusion) lose signal and appear **dark on DWI**
- The **apparent diffusion coefficient (ADC) map** quantifies diffusion — low ADC values correspond to restricted diffusion

### B-values

- The "b-value" determines the degree of diffusion weighting (measured in s/mm²)
- **b=0:** essentially a T2-weighted image (no diffusion weighting)
- **b=400–800:** typical b-values for spine DWI
- Higher b-values increase sensitivity to restricted diffusion but reduce signal-to-noise ratio

### Technical Challenges in Spine DWI

- **Susceptibility artifacts** near bone-air and bone-soft tissue interfaces
- **Motion artifacts** from CSF pulsation and patient breathing
- **Geometric distortion** — single-shot EPI (echo-planar imaging) is prone to distortion in the spine
- Newer techniques (reduced field-of-view DWI, RESOLVE) improve image quality

## Clinical Applications

### Vertebral Body Pathology

| Finding | DWI Signal | ADC Value | Interpretation |
|---------|-----------|-----------|---------------|
| **Acute benign compression fracture** | Bright (may be) | High ADC (>1.0 × 10⁻³) | Edema with free water diffusion |
| **Pathologic fracture (tumor)** | Bright | Low ADC (<1.0 × 10⁻³) | Dense tumor cellularity restricts diffusion |
| **Chronic fracture** | Isointense/dark | High ADC | No restricted diffusion |
| **Normal marrow** | Variable | Intermediate ADC | Normal background |

### Spinal Cord

- **Acute cord infarction:** restricted diffusion (bright DWI, low ADC) — analogous to brain stroke imaging
- **Cord compression without infarction:** may show T2 signal change but no restricted diffusion
- **Intramedullary abscess:** restricted diffusion in the abscess cavity
- **Epidermoid cyst vs. arachnoid cyst:** epidermoids restrict diffusion; arachnoid cysts do not

### Infection

- **Epidural abscess:** restricted diffusion within the abscess collection (bright DWI, low ADC)
- **Discitis:** may show restricted diffusion in the disc and adjacent marrow
- Helps differentiate abscess from phlegmon or reactive fluid

!!! tip "Clinical Pearl"
    The most important clinical application of spine DWI is differentiating **acute benign (osteoporotic) vertebral compression fractures from pathologic (malignant) fractures**. Both can show marrow edema on STIR. However, malignant fractures typically show restricted diffusion (low ADC <1.0 × 10⁻³ mm²/s) due to dense tumor cellularity, while benign fractures show facilitated diffusion (high ADC) due to edema. This distinction can avoid unnecessary biopsy.

## Limitations

- Image quality is lower in the spine than in the brain due to susceptibility and motion artifacts
- ADC values overlap between benign and malignant processes — not 100% specific
- Standard single-shot EPI produces significant geometric distortion in the spine
- Not yet universally included in routine spine MRI protocols
- Interpretation requires correlation with standard anatomic sequences

## Key Points

- DWI measures water molecule diffusion and provides functional tissue information
- Low ADC (restricted diffusion) suggests dense cellularity (tumor) or abscess
- High ADC (facilitated diffusion) suggests edema (benign fracture) or cyst
- Most important application: differentiating benign from malignant vertebral compression fractures
- DWI can detect acute spinal cord infarction analogous to brain DWI for stroke
- Image quality in the spine is improving with newer techniques (reduced FOV, RESOLVE)

## Related Articles

- [MRI of the Spine](mri-spine.md)
- [MRI Pulse Sequences](mri-pulse-sequences.md)
- [Gadolinium Enhancement](gadolinium-enhancement.md)
- [Spinal Cord](../anatomy/spinal-cord.md)
