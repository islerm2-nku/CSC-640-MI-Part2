---
title: "Presentations"
date: 2025-11-30
draft: false
---

# Project Presentations

This page contains presentation materials for the iRacing Telemetry API project.

## Available Presentations

### API Overview
A comprehensive overview of the API endpoints, features, and usage examples.

- [View/Download API Overview Slides](https://raw.githubusercontent.com/islerm2-nku/CSC-640-MI-Part2/main/docs/static/presentations/api-overview.md)
- [View on GitHub](https://github.com/islerm2-nku/CSC-640-MI-Part2/blob/main/docs/static/presentations/api-overview.md)

This presentation covers:
- Project architecture and tech stack
- Authentication flow with GitHub OAuth
- All API endpoints with examples
- Key features and capabilities
- LapService architecture
- Testing and deployment

---

### Deployment Guide
Step-by-step guide for deploying the application using Docker.

- [View/Download Deployment Guide Slides](https://raw.githubusercontent.com/islerm2-nku/CSC-640-MI-Part2/main/docs/static/presentations/deployment-guide.md)
- [View on GitHub](https://github.com/islerm2-nku/CSC-640-MI-Part2/blob/main/docs/static/presentations/deployment-guide.md)

This guide covers:
- Prerequisites and setup
- Docker deployment steps
- OAuth configuration
- Database verification
- Troubleshooting
- Testing authentication

---

## Viewing the Presentations

These presentations are created with [Marp](https://marp.app/), a Markdown-based slide deck tool.

### Options for viewing:

**Option 1: Install Marp CLI and export to HTML**
```bash
# Install Marp CLI
npm install -g @marp-team/marp-cli

# Export to HTML
marp docs/static/presentations/api-overview.md -o docs/static/presentations/api-overview.html
marp docs/static/presentations/deployment-guide.md -o docs/static/presentations/deployment-guide.html
```

**Option 2: Use Marp VS Code Extension**
- Install the [Marp for VS Code](https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode) extension
- Open the .md files and click "Open Preview" to view the slides

**Option 3: View as Markdown**
- Download the .md files and view them in any Markdown editor
- The content is structured with `---` separators between slides

---

## Related Documentation

- [README](/README.md) - Project overview and quick start
- [API Documentation](http://localhost/docs) - Interactive API docs (when running locally)
