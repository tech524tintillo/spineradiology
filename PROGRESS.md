# SpineRadiology.com — Progress Report
**Updated:** March 19, 2026

## Status: 71/220 articles complete (3/12 categories)

## Build Notes
- After every mkdocs build: cp ~/Downloads/landing.html site/index.html
- Wikimedia blocks curl — save images manually from browser
- Images use figure tags with captions, centered, width constrained
- CSS white background on images for dark theme readability
- All content must be original (Avery requirement)

## Category 1: Anatomy — 25/25 DONE (16 images)
## Category 2: Imaging Modalities — 15/15 DONE (awaiting Avery images)
## Category 3: Degenerative Disease — 31/31 DONE (3 images + awaiting Avery)
## Categories 4-12: NOT STARTED (149 articles)

## Key Commits
- ddccacb Batch 1 anatomy
- 40488ba Batch 1 images fixed
- a21e4bd Batch 2 + images
- 3bf6d7f Category 2 Imaging Modalities
- d135b3a Category 3 Degenerative Disease
- a2e4147 Category 3 images

## TODO
- Landing page overwrites on build
- Awaiting Avery clinical images (Cat 2 + Cat 3)
- 9 anatomy articles need images
- Avery content review
- Resize dermatome-map.png (3.8MB)
- Next: Category 4 Trauma
