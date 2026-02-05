# Upload Runtime Packages to GitHub Releases

## Overview

The runtime packages (Python, Node.js, AI models) are too large for GitHub Pages (100MB limit).
They must be uploaded to a GitHub Release instead.

## Files to Upload

Location: `Synthesis.Pro/Runtime/Packages/`

- `python-embedded.zip` (380 MB)
- `node-embedded.zip` (25 MB)
- `models.zip` (295 MB)

## Steps to Upload

### Using GitHub Web Interface

1. **Go to Releases**
   ```
   https://github.com/Fallen-Entertainment/Synthesis.Pro/releases
   ```

2. **Create New Release**
   - Click "Draft a new release"
   - Tag version: `v1.1.0-runtime-deps`
   - Target: `main`
   - Release title: `Runtime Dependencies v1.1.0`
   - Description:
     ```markdown
     Runtime dependencies for Synthesis.Pro v1.1.0

     **Included:**
     - Python 3.11.0 embedded runtime with site-packages
     - Node.js 18.19.0 runtime
     - AI models for RAG system

     **Auto-downloaded by FirstTimeSetup.cs on package import**

     These files support the download-on-demand system for Asset Store compliance.
     ```

3. **Upload Files**
   - Drag and drop the three zip files from `Synthesis.Pro/Runtime/Packages/`
   - OR click "Attach binaries" and select them

4. **Publish Release**
   - Click "Publish release"

### Using GitHub CLI

```bash
# Create release
gh release create v1.1.0-runtime-deps \
  --title "Runtime Dependencies v1.1.0" \
  --notes "Runtime dependencies for Synthesis.Pro v1.1.0"

# Upload files
cd "Synthesis.Pro/Runtime/Packages"
gh release upload v1.1.0-runtime-deps \
  python-embedded.zip \
  node-embedded.zip \
  models.zip
```

## Verify Upload

After publishing, verify the URLs work:

```bash
# Test each download
curl -I https://github.com/Fallen-Entertainment/Synthesis.Pro/releases/download/v1.1.0-runtime-deps/python-embedded.zip
curl -I https://github.com/Fallen-Entertainment/Synthesis.Pro/releases/download/v1.1.0-runtime-deps/node-embedded.zip
curl -I https://github.com/Fallen-Entertainment/Synthesis.Pro/releases/download/v1.1.0-runtime-deps/models.zip
```

All should return `302 Found` or `200 OK`.

## Code Configuration

FirstTimeSetup.cs has been updated to use these URLs:

```csharp
// Assets/Synthesis.Pro/Editor/FirstTimeSetup.cs:17-19
private const string PYTHON_DOWNLOAD_URL = "https://github.com/Fallen-Entertainment/Synthesis.Pro/releases/download/v1.1.0-runtime-deps/python-embedded.zip";
private const string NODE_DOWNLOAD_URL = "https://github.com/Fallen-Entertainment/Synthesis.Pro/releases/download/v1.1.0-runtime-deps/node-embedded.zip";
private const string MODELS_DOWNLOAD_URL = "https://github.com/Fallen-Entertainment/Synthesis.Pro/releases/download/v1.1.0-runtime-deps/models.zip";
```

## Testing

After upload, test FirstTimeSetup:

1. Open clean Unity project
2. Import Synthesis.Pro package
3. Tools → Synthesis → Setup → First Time Setup
4. Verify downloads complete successfully

## Updating Runtime Packages

For future versions:

1. Run `build-runtime-packages.ps1` to rebuild packages
2. Create new release: `v1.2.0-runtime-deps`
3. Upload new zip files
4. Update URLs in FirstTimeSetup.cs
5. Tag and release main package

---

**Created:** 2026-02-03
**Purpose:** Asset Store compliance via download-on-demand
