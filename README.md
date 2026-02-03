# Synthesis.Pro - GitHub Pages

This branch hosts the GitHub Pages site for Synthesis.Pro distribution.

## Structure

```
/
├── index.html           # Landing page
├── version.json         # Update manifest for version checking
├── downloads/           # Large dependencies
│   ├── python-embedded.zip  (~50MB)
│   └── models.zip           (~200MB)
└── api/
    └── sync/           # Public DB sync endpoints (optional)
```

## Files

### version.json
Contains the latest version info for the Unity update checker.

**Format:**
```json
{
  "version": "1.1.0",
  "url": "https://github.com/.../releases/download/v1.1.0/Synthesis.Pro.unitypackage",
  "notes": "Release notes..."
}
```

**Updated by:** GitHub Actions workflow on release

### downloads/
Large dependency files downloaded by FirstTimeSetup.cs on first import:
- `python-embedded.zip` - Embedded Python 3.11 runtime
- `models.zip` - AI embedding models

### api/sync/
Optional sync endpoints for public knowledge base sharing (future implementation).

## Usage

This site is accessed by:
- Unity Editor update checker
- First-time setup dependency downloader
- Users browsing for latest version

## Maintenance

**To update version.json manually:**
```bash
git checkout gh-pages
# Edit version.json
git add version.json
git commit -m "Update version to X.Y.Z"
git push origin gh-pages
```

**Note:** GitHub Actions automatically updates this on tagged releases.

---

Visit: https://fallen-entertainment.github.io/Synthesis.Pro/
