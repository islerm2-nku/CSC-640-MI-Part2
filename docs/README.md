# Hugo Documentation Site

This directory contains the Hugo static site for project documentation.

## Local Development

```bash
cd docs
hugo server -D
```

Visit http://localhost:1313 to view the site.

## Building for Production

```bash
cd docs
hugo
```

The static site will be generated in `docs/public/`.

## GitHub Pages Deployment

To deploy to GitHub Pages:

1. Build the site:
   ```bash
   cd docs
   hugo
   ```

2. The site will be in `public/` directory

3. Configure GitHub Pages to serve from the `docs/public` directory or create a GitHub Actions workflow

### GitHub Actions Workflow (Recommended)

Create `.github/workflows/hugo.yml`:

```yaml
name: Deploy Hugo site to Pages

on:
  push:
    branches: ["main"]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          submodules: recursive
      
      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v2
        with:
          hugo-version: 'latest'
      
      - name: Build
        run: cd docs && hugo --minify
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./docs/public
  
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

## Presentations

The Marp presentation files are stored in `static/presentations/`:
- `api-overview.md` - API overview and features
- `deployment-guide.md` - Deployment instructions

These files are accessible at:
- `/presentations/api-overview.md`
- `/presentations/deployment-guide.md`

## Theme

This site uses the [Hugo Book](https://github.com/alex-shpak/hugo-book) theme.
