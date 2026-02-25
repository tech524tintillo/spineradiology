# SpineRadiology.com

A comprehensive wiki and reference for spine radiology built with MkDocs Material.

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run local dev server
mkdocs serve

# Build static site
mkdocs build
```

The local dev server runs at `http://127.0.0.1:8000`.

## Deployment to Cloudflare Pages

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/spineradiology.git
git push -u origin main
```

### 2. Set up Cloudflare Pages

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/) → Pages → Create a project
2. Connect your GitHub account and select the `spineradiology` repository
3. Configure build settings:
   - **Build command:** `pip install -r requirements.txt && mkdocs build`
   - **Build output directory:** `site`
   - **Python version:** Set environment variable `PYTHON_VERSION` = `3.11`
4. Click **Save and Deploy**

### 3. Point the Domain (Squarespace DNS)

1. In Cloudflare Pages → Custom domains → Add `spineradiology.com`
2. Cloudflare will give you a CNAME target (e.g., `spineradiology.pages.dev`)
3. Log in to Squarespace Domains → DNS Settings for spineradiology.com
4. Add a CNAME record:
   - **Host:** `www`
   - **Points to:** `spineradiology.pages.dev`
5. For the root domain (spineradiology.com without www):
   - Add a CNAME record with **Host:** `@` pointing to `spineradiology.pages.dev`
   - OR transfer DNS to Cloudflare for easier management (recommended)

### 4. SSL

Cloudflare Pages provides free SSL automatically. No configuration needed.

## Project Structure

```
spineradiology/
├── mkdocs.yml              # Site configuration and navigation
├── requirements.txt        # Python dependencies
├── docs/
│   ├── index.md            # Homepage
│   ├── assets/
│   │   ├── css/custom.css  # Custom styles
│   │   └── images/         # Site images
│   ├── anatomy/            # Spine anatomy articles
│   ├── imaging-modalities/ # Imaging technique articles
│   ├── degenerative-disease/
│   ├── trauma/
│   ├── neoplasms/
│   ├── infection/
│   ├── inflammatory-autoimmune/
│   ├── congenital-developmental/
│   ├── vascular/
│   ├── metabolic-systemic/
│   ├── post-surgical-spine/
│   └── special-topics/
└── site/                   # Built site (generated, gitignored)
```

## Adding Content

Each article is a Markdown file in the appropriate category folder. To add or update an article:

1. Edit the `.md` file in the category folder
2. Commit and push to GitHub
3. Cloudflare Pages will automatically rebuild and deploy

## Content Status

- **Total articles:** 220
- **Categories:** 12
- Articles are placeholders until reviewed and populated with content.
