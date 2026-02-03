# Automated Release Guide

This repository uses GitHub Actions to automate Unity package releases.

## Setup (One-time)

### 1. Add Unity Credentials to GitHub Secrets

Go to: `Settings > Secrets and variables > Actions`

Add these secrets:
- `UNITY_LICENSE` - Your Unity license file content
- `UNITY_EMAIL` - Your Unity account email
- `UNITY_PASSWORD` - Your Unity account password

**To get your Unity license:**
```bash
# Run Unity in batch mode to generate license
Unity.exe -batchmode -createManualActivationFile
# Upload the file to https://license.unity3d.com/manual
# Download the .ulf file
# Copy its contents to the UNITY_LICENSE secret
```

### 2. Enable GitHub Pages

1. Go to: `Settings > Pages`
2. Source: Deploy from branch
3. Branch: `gh-pages`
4. Save

## How to Release a New Version

### Simple 3-Step Process:

1. **Update version in code:**
   ```csharp
   // Assets/Synthesis.Pro/Editor/SynthesisEditorTools.cs
   private const string CURRENT_VERSION = "1.2.0"; // Update this
   ```

2. **Commit and tag:**
   ```bash
   git add .
   git commit -m "Release v1.2.0"
   git tag v1.2.0
   git push origin main
   git push origin v1.2.0
   ```

3. **That's it!** GitHub Actions will:
   - Build the Unity package
   - Create a GitHub Release
   - Upload the `.unitypackage` file
   - Update `version.json` on GitHub Pages

## What Happens Automatically

```
Push tag v1.2.0
    ↓
GitHub Actions starts
    ↓
Exports Unity package
    ↓
Creates Release v1.2.0
    ↓
Uploads Synthesis.Pro.unitypackage
    ↓
Updates version.json on gh-pages
    ↓
Users can now update via Unity!
```

## Manual Export (Optional)

You can also export manually in Unity:

1. Open Unity
2. Go to: `Synthesis > Export Package`
3. Package saved as `Synthesis.Pro.unitypackage`

## Checking It Works

After releasing v1.2.0:

1. Check GitHub Releases page
2. Verify `version.json` updated:
   ```
   https://fallen-entertainment.github.io/Synthesis.Pro/version.json
   ```
3. Open Unity with v1.1.0
4. Click `Synthesis > Check for Updates`
5. Should show: "Update Available! v1.2.0"

## Troubleshooting

**Build fails?**
- Check Unity secrets are set correctly
- Verify Unity version compatibility

**Package not uploaded?**
- Check GitHub Actions logs
- Verify export script exists

**version.json not updating?**
- Check gh-pages branch exists
- Verify GitHub Pages is enabled

## File Structure

```
.github/
├── workflows/
│   └── release.yml          # Automated workflow
└── RELEASE_GUIDE.md         # This file

Assets/Synthesis.Pro/Editor/
└── ExportPackage.cs         # Unity export script
```

## Version Numbering

Use semantic versioning: `MAJOR.MINOR.PATCH`

- `MAJOR` - Breaking changes (2.0.0)
- `MINOR` - New features (1.2.0)
- `PATCH` - Bug fixes (1.1.1)

## Release Checklist

Before tagging:
- [ ] Update CURRENT_VERSION in code
- [ ] Test the build locally
- [ ] Update changelog/release notes
- [ ] Commit changes
- [ ] Create and push tag
- [ ] Verify GitHub Actions succeeds
- [ ] Test update checker in Unity

---

**Need help?** Check GitHub Actions logs for detailed build output.
