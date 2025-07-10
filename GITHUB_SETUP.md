# GitHub Repository Setup Guide

This guide will help you prepare and publish the MCP Nautobot Server to GitHub.

## 🚨 Pre-Release Security Checklist

**CRITICAL**: Before pushing to GitHub, ensure you have:

- [x] Removed `.env` file containing API credentials
- [x] Removed `public_ips.json` containing network data
- [x] Updated `.gitignore` to exclude sensitive files
- [ ] Revoked the exposed Nautobot API token
- [ ] Reviewed all code for hardcoded credentials
- [ ] Checked test files for production data

## 📋 Repository Setup Steps

### 1. Initialize Git Repository

```bash
cd /Users/admin/Documents/projects/mcp-nautobot
git init
git add .
git commit -m "Initial commit: MCP Nautobot Server v1.0.0"
```

### 2. Create GitHub Repository

1. Go to [GitHub](https://github.com/new)
2. Repository name: `mcp-nautobot`
3. Description: "Model Context Protocol server for Nautobot network automation"
4. Set to **Public** (for open source)
5. **Do NOT** initialize with README (we have one)
6. License: MIT (already included)

### 3. Push to GitHub

```bash
git remote add origin https://github.com/yourusername/mcp-nautobot.git
git branch -M main
git push -u origin main
```

### 4. Configure Repository Settings

In GitHub repository settings:

#### General
- [ ] Add topics: `mcp`, `nautobot`, `network-automation`, `ai`, `claude`
- [ ] Set website: `https://modelcontextprotocol.io`

#### Collaborators & Teams
- [ ] Add any initial collaborators

#### Security
- [ ] Enable Dependabot alerts
- [ ] Enable Dependabot security updates
- [ ] Set up code scanning (optional)

#### Pages (optional)
- [ ] Enable GitHub Pages from `/docs` folder if adding documentation site

### 5. Create Initial Release

1. Go to Releases → "Create a new release"
2. Tag: `v1.0.0`
3. Title: "MCP Nautobot Server v1.0.0 - Initial Release"
4. Copy content from `RELEASE_NOTES.md`
5. Attach any binaries if applicable
6. Mark as "Pre-release" initially if desired

### 6. Set Up GitHub Actions (Optional)

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    - name: Run tests
      run: |
        pytest
    - name: Check code style
      run: |
        black --check src/ tests/
        isort --check-only src/ tests/
```

### 7. Community Setup

- [ ] Create initial Issues for roadmap items
- [ ] Add "good first issue" labels to appropriate tasks
- [ ] Create a Discussion for general questions
- [ ] Pin important issues/discussions

### 8. Documentation

Consider adding:
- [ ] Wiki pages for advanced topics
- [ ] Example configurations
- [ ] Video tutorial (link in README)

## 🎯 Post-Release Tasks

1. **Announce the Release**:
   - [ ] Post on relevant forums (Nautobot, Network Automation)
   - [ ] Share on social media
   - [ ] Submit to MCP tool directory

2. **Monitor Initial Feedback**:
   - [ ] Watch for issues
   - [ ] Respond to questions
   - [ ] Plan first patch release

3. **Build Community**:
   - [ ] Recognize early contributors
   - [ ] Create contributor guidelines
   - [ ] Set up regular release cycle

## 📦 Publishing to PyPI (Future)

When ready to publish to PyPI:

```bash
# Build the package
python -m build

# Upload to TestPyPI first
python -m twine upload --repository testpypi dist/*

# Test installation
pip install -i https://test.pypi.org/simple/ mcp-nautobot-server

# Upload to PyPI
python -m twine upload dist/*
```

## 🔗 Useful Links

- [GitHub Docs](https://docs.github.com/)
- [Open Source Guide](https://opensource.guide/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)

---

Remember: The security of the network infrastructure data is paramount. Always double-check for sensitive information before making the repository public.