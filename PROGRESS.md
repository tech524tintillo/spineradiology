# SpineRadiology.com — Progress Report
**Updated:** March 19, 2026

## Status: 40/220 articles (2/12 categories)

## Build Notes
- After every `mkdocs build`, run: `cp ~/Downloads/landing.html site/index.html`
- Wikimedia blocks curl — save images manually from browser
- Images use `<figure>` tags with captions, centered, width constrained
- CSS adds white background to images for dark theme readability
- All content must be original (Avery's requirement)

## Category 1: Anatomy — 25/25 DONE
- Batch 1 (1-10): Content + images (Gray's Anatomy plates, public domain)
- Batch 2 (11-25): Content done, 6 of 15 have images
- Images in: docs/assets/images/anatomy/

## Category 2: Imaging Modalities — 15/15 DONE
- All articles written, no images yet
- Message sent to Avery requesting his anonymized cases
- Priority images: lateral C-spine XR, sagittal CT, sagittal T2 MRI, T1 vs T2, pre/post gadolinium

## Categories 3-12: NOT STARTED (180 articles)
- 3. Degenerative Disease (~30) — NEXT
- 4. Trauma (~30)
- 5. Neoplasms (~25)
- 6. Infection (~12)
- 7. Inflammatory/Autoimmune (~12)
- 8. Congenital/Developmental (~18)
- 9. Vascular (~10)
- 10. Metabolic/Systemic (~12)
- 11. Post-Surgical Spine (~15)
- 12. Special Topics (~15)

## Key Git Commits
- ddccacb — Batch 1 anatomy articles
- 40488ba — All Batch 1 images fixed
- a21e4bd — Batch 2 articles + images + captions
- 3bf6d7f — Category 2 Imaging Modalities

## TODO
- Landing page overwrites on build — need permanent fix
- 9 Batch 2 anatomy articles need images
- Imaging Modalities awaiting Avery's images
- Avery needs to review all content
- Resize dermatome-map.png (3.8MB)
