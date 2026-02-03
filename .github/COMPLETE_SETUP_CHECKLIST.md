# Complete Setup Checklist

Everything you need to get Synthesis.Pro ready for release.

## Pre-Release Checklist

### ✅ Phase 1: GitHub Pages Setup (30 mins)

Follow: [SETUP_GITHUB_PAGES.md](SETUP_GITHUB_PAGES.md)

- [ ] Create `gh-pages` branch
- [ ] Enable GitHub Pages in repo settings
- [ ] Upload `version.json`
- [ ] Test: https://fallen-entertainment.github.io/Synthesis.Pro/version.json

**Downloads (choose one approach):**

**Option A: GitHub Pages** (easier, but 100MB limit per file)
- [ ] Prepare `python-embedded.zip` (~50MB)
- [ ] Prepare `models.zip` (~100-200MB)
- [ ] Upload to `downloads/` folder
- [ ] Test download URLs work

**Option B: GitHub Releases** (better for large files)
- [ ] Prepare zip files
- [ ] Create release: `v1.0.0-deps`
- [ ] Upload as release assets
- [ ] Update URLs in `FirstTimeSetup.cs`

---

### ✅ Phase 2: Unity Secrets (15 mins)

Follow: [SETUP_UNITY_SECRETS.md](SETUP_UNITY_SECRETS.md)

- [ ] Generate Unity license file (.ulf)
- [ ] Add `UNITY_LICENSE` secret to GitHub
- [ ] Add `UNITY_EMAIL` secret to GitHub
- [ ] Add `UNITY_PASSWORD` secret to GitHub
- [ ] Test workflow runs successfully

---

### ✅ Phase 3: Code Updates (5 mins)

Update version and URLs:

1. **Update current version:**
   ```csharp
   // Assets/Synthesis.Pro/Editor/SynthesisEditorTools.cs:114
   private const string CURRENT_VERSION = "1.1.0";
   ```

2. **Verify download URLs:**
   ```csharp
   // Assets/Synthesis.Pro/Editor/FirstTimeSetup.cs:8-9
   private const string PYTHON_DOWNLOAD_URL = "https://fallen-entertainment.github.io/Synthesis.Pro/downloads/python-embedded.zip";
   private const string MODELS_DOWNLOAD_URL = "https://fallen-entertainment.github.io/Synthesis.Pro/downloads/models.zip";
   ```

3. **Verify update check URL:**
   ```csharp
   // Assets/Synthesis.Pro/Editor/SynthesisEditorTools.cs:115
   private const string UPDATE_CHECK_URL = "https://fallen-entertainment.github.io/Synthesis.Pro/version.json";
   ```

- [ ] Version number updated
- [ ] URLs match your GitHub Pages
- [ ] Code compiles without errors

---

### ✅ Phase 4: Test Locally (10 mins)

Before pushing, test everything:

**Test 1: Package Export**
- [ ] Unity → `Synthesis > Export Package`
- [ ] `Synthesis.Pro.unitypackage` created
- [ ] No errors in console

**Test 2: Update Checker**
- [ ] Unity → `Synthesis > Check for Updates`
- [ ] Connects to server (or shows offline)
- [ ] No crashes

**Test 3: Data Management**
- [ ] Unity → `Synthesis > Data Management > Backup`
- [ ] Works without errors
- [ ] File created

---

### ✅ Phase 5: First Release (10 mins)

Time to go live!

```bash
# 1. Commit everything
git add .
git commit -m "Release v1.1.0: Complete distribution system"

# 2. Push to main
git push origin main

# 3. Create and push tag
git tag v1.1.0
git push origin v1.1.0
```

**What happens next:**
1. GitHub Actions triggers
2. Unity package built
3. Release created
4. Package uploaded
5. version.json updated

- [ ] Tag pushed successfully
- [ ] GitHub Actions workflow started
- [ ] Check: Actions tab on GitHub

---

### ✅ Phase 6: Verify Release (5 mins)

After GitHub Actions completes:

**Check Release:**
- [ ] Go to: `Releases` tab on GitHub
- [ ] Release `v1.1.0` exists
- [ ] `Synthesis.Pro.unitypackage` attached
- [ ] Release notes look good

**Check version.json:**
- [ ] Visit: https://fallen-entertainment.github.io/Synthesis.Pro/version.json
- [ ] Shows version `1.1.0`
- [ ] URL points to release asset

**Test Downloads:**
```bash
# Test package download
curl -I https://github.com/Fallen-Entertainment/Synthesis.Pro/releases/download/v1.1.0/Synthesis.Pro.unitypackage

# Test Python (if on GitHub Pages)
curl -I https://fallen-entertainment.github.io/Synthesis.Pro/downloads/python-embedded.zip

# Test models (if on GitHub Pages)
curl -I https://fallen-entertainment.github.io/Synthesis.Pro/downloads/models.zip
```

- [ ] All URLs return `200 OK`
- [ ] File sizes look correct

---

### ✅ Phase 7: Test Installation (15 mins)

**Fresh Unity Project Test:**

1. Create new Unity project
2. Download `Synthesis.Pro.unitypackage` from releases
3. Import into Unity
4. Watch first-time setup run
5. Verify:
   - [ ] Databases created
   - [ ] Python downloaded (or skipped)
   - [ ] Models downloaded (or skipped)
   - [ ] No critical errors
   - [ ] Menu items appear
   - [ ] `Synthesis > Check for Updates` works

---

## Quick Reference

### URLs You'll Need

Replace these with your actual values:

```
Repository:     https://github.com/Fallen-Entertainment/Synthesis.Pro
GitHub Pages:   https://fallen-entertainment.github.io/Synthesis.Pro/
version.json:   https://fallen-entertainment.github.io/Synthesis.Pro/version.json
Latest Release: https://github.com/Fallen-Entertainment/Synthesis.Pro/releases/latest
```

### File Locations

```
Code:
├── Assets/Synthesis.Pro/Editor/
│   ├── SynthesisEditorTools.cs    (version + update URL)
│   ├── FirstTimeSetup.cs          (download URLs)
│   ├── ExportPackage.cs           (package builder)
│   └── PublicDBSync.cs            (sync system)

Workflows:
├── .github/workflows/
│   └── release.yml                (automated builds)

Documentation:
├── .github/
│   ├── SETUP_GITHUB_PAGES.md
│   ├── SETUP_UNITY_SECRETS.md
│   ├── RELEASE_GUIDE.md
│   └── DISTRIBUTION_SYSTEM.md
```

---

## Troubleshooting

### GitHub Actions Fails

1. Check Actions logs on GitHub
2. Verify Unity secrets are set
3. Ensure Unity version matches project
4. Try manual export first

### Downloads Fail

1. Verify files uploaded to gh-pages
2. Check URLs match in code
3. Test URLs in browser
4. Check file size limits (100MB on GitHub Pages)

### First-Time Setup Fails

1. Check Unity console for errors
2. Verify download URLs
3. Test downloads manually
4. Check internet connection

---

## After First Release

### Releasing Updates

Simple 3-step process:

```bash
# 1. Update version in code
# Edit: CURRENT_VERSION = "1.2.0"

# 2. Commit and tag
git add .
git commit -m "Release v1.2.0"
git tag v1.2.0
git push origin main --tags

# 3. Done! GitHub Actions does the rest
```

### Monitoring

Check these regularly:
- [ ] GitHub Actions status
- [ ] Release download counts
- [ ] User feedback/issues
- [ ] Bandwidth usage

---

## Estimated Timeline

- **Phase 1** (GitHub Pages): 30 mins
- **Phase 2** (Unity Secrets): 15 mins
- **Phase 3** (Code Updates): 5 mins
- **Phase 4** (Local Tests): 10 mins
- **Phase 5** (First Release): 10 mins
- **Phase 6** (Verify Release): 5 mins
- **Phase 7** (Test Install): 15 mins

**Total: ~90 minutes for complete setup**

Future releases: ~5 minutes (just tag and push!)

---

## Success Criteria

You're done when:

✅ GitHub Pages site is live
✅ version.json accessible
✅ Downloads available (Python + models)
✅ Unity secrets configured
✅ First release on GitHub
✅ Package downloads successfully
✅ First-time setup works
✅ Update checker works
✅ No critical errors

**Then you're ready for users! 🎉**

---

## Need Help?

1. Check documentation in `.github/` folder
2. Review GitHub Actions logs
3. Test each component individually
4. Open an issue if stuck

---

## Next Steps

After setup is complete:

1. **Announce release** on your channels
2. **Monitor feedback** from early users
3. **Plan next version** features
4. **Keep iterating!**

Welcome to automated releases! 🚀
