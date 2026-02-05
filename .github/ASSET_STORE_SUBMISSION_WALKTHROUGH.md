# Asset Store Submission - Complete Walkthrough

**Status:** In Progress
**Estimated Time:** 1 hour total
**Goal:** Submit Synthesis.Pro v1.1.0-beta to Unity Asset Store

---

## Phase 1: Upload Runtime Packages to GitHub (10 mins)

**Why:** The runtime packages are too large for GitHub Pages (100MB limit). GitHub Releases can host files up to 2GB.

### Step 1: Create the Release

1. Open your browser to:
   ```
   https://github.com/Fallen-Entertainment/Synthesis.Pro/releases
   ```

2. Click **"Draft a new release"** (top right)

3. Fill in the form:
   - **Tag version:** `v1.1.0-runtime-deps`
   - **Target:** `main` (should be default)
   - **Release title:** `Runtime Dependencies v1.1.0`
   - **Description:**
     ```markdown
     Runtime dependencies for Synthesis.Pro v1.1.0

     **Included:**
     - Python 3.11.0 embedded runtime with site-packages
     - Node.js 18.19.0 runtime
     - AI models for RAG system

     **Auto-downloaded by FirstTimeSetup.cs on package import**

     These files support the download-on-demand system for Asset Store compliance.
     ```

### Step 2: Upload the Files

4. Scroll down to **"Attach binaries by dropping them here or selecting them"**

5. Navigate to `d:\Unity Projects\Synthesis.Pro\Synthesis.Pro\Runtime\Packages\`

6. Drag and drop all three files:
   - `python-embedded.zip` (380 MB) - will take ~2-3 minutes to upload
   - `node-embedded.zip` (25 MB) - will take ~30 seconds
   - `models.zip` (295 MB) - will take ~2 minutes

7. Wait for uploads to complete (green checkmarks appear)

8. Click **"Publish release"** at the bottom

**Why separate release?** This keeps runtime dependencies separate from code releases. When you update Synthesis.Pro code to v1.2.0, the runtimes stay at v1.1.0 unless they need updating.

---

## Phase 2: Verify Download URLs (2 mins)

**Why:** Ensure FirstTimeSetup can actually download the files before testing in Unity.

### Test URLs

Open PowerShell and run:

```powershell
# Test Python download
curl -I https://github.com/Fallen-Entertainment/Synthesis.Pro/releases/download/v1.1.0-runtime-deps/python-embedded.zip

# Test Node.js download
curl -I https://github.com/Fallen-Entertainment/Synthesis.Pro/releases/download/v1.1.0-runtime-deps/node-embedded.zip

# Test Models download
curl -I https://github.com/Fallen-Entertainment/Synthesis.Pro/releases/download/v1.1.0-runtime-deps/models.zip
```

**What to look for:**
- Each command should return `HTTP/2 302` (redirect) or `HTTP/2 200` (OK)
- If you see `404 Not Found`, the release isn't published yet or file names don't match

**Example good output:**
```
HTTP/2 302
location: https://objects.githubusercontent.com/...
content-type: application/zip
```

---

## Phase 3: Test FirstTimeSetup (15 mins)

**Why:** Verify the download-on-demand system works before submission.

### Step 1: Create Clean Test Project

1. Open Unity Hub
2. Click **"New project"**
3. Name: `SynthesisProTest`
4. Template: 3D Core
5. Click **"Create project"**
6. Wait for Unity to open

### Step 2: Export Current Package

Back in your main Synthesis.Pro Unity project:

1. **Tools → Synthesis → Export Package**
2. This creates `Synthesis.Pro.unitypackage` in project root
3. Note the location

### Step 3: Import and Test

In the clean test project:

1. **Assets → Import Package → Custom Package**
2. Navigate to `Synthesis.Pro.unitypackage`
3. Click **"Import"**
4. **"Import all"** in the dialog
5. Wait for import to complete

### Expected Behavior

```
[Synthesis] Running first-time setup...
Welcome to Synthesis.Pro Beta! (dialog appears)
Click "Yes, Set Up"
Progress bar appears:
  → Creating databases... 20%
  → Downloading Python runtime... 30%
  → Downloading Node.js runtime... 50%
  → Downloading AI models... 70%
  → Setting up Python environment... 80%
  → Creating initial content... 90%
Setup Complete! (dialog appears)
```

### Step 4: Verify Installation

In the test project:

1. Check folders exist:
   - `Assets/Synthesis.Pro/KnowledgeBase/python/python.exe` ✅
   - `Assets/Synthesis.Pro/Server/node/node.exe` ✅
   - `Synthesis.Pro/Server/models/unsloth/` ✅ (outside Assets, in project root)

2. Check console for errors:
   - Look for `[Synthesis] ✅` success messages
   - No red errors allowed
   - Yellow warnings are okay

3. Check menu exists:
   - **Tools → Synthesis** menu appears ✅

### Troubleshooting

**If something fails:**
- Check Unity Console for error messages
- Verify URLs are accessible (Phase 2)
- Check internet connection
- Try **Tools → Synthesis → Setup → First Time Setup** manually

---

## Phase 4: Update Documentation (2 mins)

**Why:** Document that runtime packages are uploaded and tested.

Mark these items complete in `Assets/Synthesis.Pro/Documentation/Product/SUBMISSION_STATUS.md`:

```markdown
- [x] Runtime packages uploaded to GitHub Releases
- [x] FirstTimeSetup tested with release URLs
- [x] Final test in clean Unity project
```

---

## Phase 5: Commit and Tag for Beta Release (5 mins)

**Why:** Version control tracks changes, and the tag enables automated releases (when Unity Pro/Plus is available).

### Step 1: Review Changes

```bash
git status
```

You should see:
```
modified:   Assets/Synthesis.Pro/Editor/FirstTimeSetup.cs
modified:   Assets/Synthesis.Pro/Documentation/Product/SUBMISSION_STATUS.md
new file:   .github/UPLOAD_RUNTIME_PACKAGES.md
new file:   .github/ASSET_STORE_SUBMISSION_WALKTHROUGH.md
modified:   Assets/Synthesis.Pro/.devlog/DEVELOPER_LOG.md
```

### Step 2: Commit

```bash
git add Assets/Synthesis.Pro/Editor/FirstTimeSetup.cs
git add Assets/Synthesis.Pro/Documentation/Product/SUBMISSION_STATUS.md
git add .github/UPLOAD_RUNTIME_PACKAGES.md
git add .github/ASSET_STORE_SUBMISSION_WALKTHROUGH.md
git add Assets/Synthesis.Pro/.devlog/DEVELOPER_LOG.md

git commit -m "$(cat <<'EOF'
Asset Store prep: Runtime packages via GitHub Releases

- Update FirstTimeSetup URLs to use GitHub Releases (exceeds GitHub Pages 100MB limit)
- Upload python-embedded.zip (380MB), node-embedded.zip (25MB), models.zip (295MB)
- Add upload guide and submission walkthrough to .github/
- Test FirstTimeSetup download-on-demand in clean project
- Update submission checklist and developer log

Ready for beta testing with NB community.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

### Step 3: Tag Beta Version

```bash
# Tag the beta version
git tag v1.1.0-beta

# Push everything
git push origin main
git push origin v1.1.0-beta
```

**What this does:**
- Saves your changes to git history
- Creates a tagged snapshot called `v1.1.0-beta`
- Makes the tag available on GitHub for reference

**Note:** This is a beta tag, not the main release. When you're ready for full release, you'll tag `v1.1.0` (without `-beta`).

---

## Phase 6: Export Package for Distribution (3 mins)

**Why:** Create the .unitypackage file that users will import.

### Option A: Via Unity Menu (Recommended)

In Unity:

1. **Tools → Synthesis → Export Package**
2. Check console: `[Export] Package exported: Synthesis.Pro.unitypackage`
3. File created at: `d:\Unity Projects\Synthesis.Pro\Synthesis.Pro.unitypackage`

### Option B: Manual Export

If the menu doesn't work:

1. **Assets → Export Package**
2. Select **entire `Synthesis.Pro` folder**
3. **Deselect** any test files or editor-only stuff
4. Click **"Export"**
5. Save as `Synthesis.Pro.unitypackage`

### What's Included/Excluded

**Excluded automatically:**
- `.git` folder
- `Synthesis.Pro/Server/` folder (outside Assets, not included)
- `.exe` files (already removed)
- Test projects

**Included:**
- All C# scripts
- Documentation
- Third-Party Notices
- Editor tools
- DLL files (compliant)

---

## Phase 7: Asset Store Submission (30 mins)

**Why:** Get Synthesis.Pro into the Asset Store for the NB community.

### Step 1: Prepare Asset Store Account

1. Go to: https://publisher.unity.com/
2. Sign in with your Unity account
3. **Create New Package** (if first submission)

### Step 2: Upload Package

1. Click **"Upload Package"** button
2. Select `Synthesis.Pro.unitypackage`
3. Wait for upload (may take 5-10 minutes for ~100MB)

### Step 3: Fill in Package Details

#### Basic Info
- **Name:** Synthesis.Pro
- **Category:** Editor Extensions → Utilities
- **Price:** Free (for beta) or set your price
- **Version:** 1.1.0-beta

#### Description

Use the template from `Assets/Synthesis.Pro/Documentation/Product/ASSET_STORE_DESCRIPTION_TEMPLATE.md`

**Key points to include:**
- ⚠️ Third-party API requirements (MUST be at top)
- Anthropic Claude API costs
- Feature overview
- Privacy architecture (dual database)
- Installation instructions

#### Screenshots/Media
- Unity Editor screenshots showing Synthesis in action
- Feature highlights
- Knowledge base interface

#### Technical Details
- **Unity Version:** 2020.3 or higher (verify your minimum supported version)
- **Supported Platforms:** Windows (initially)
- **Dependencies:** None within Unity (runtime dependencies downloaded automatically)

### Step 4: Cover Letter (Important!)

In the "Notes to Reviewers" or submission notes field, include:

```
Asset Store Review Team,

This package implements a download-on-demand system for runtime dependencies (Python, Node.js, AI models) to comply with Section 1.5.a (no executables in package).

Technical Approach:
- Package contains NO .exe files
- Runtime dependencies downloaded from GitHub Releases on first setup
- Total download size: ~700MB (one-time, on user's request)
- All downloads from trusted official sources with user consent

Functional Necessity:
- Python/Node.js required for AI/ML functionality
- Cannot execute natively in Unity C# environment
- Similar to other native plugin packages (FFmpeg, OpenCV)

Legal Basis:
- Unity Asset Store EULA permits downloading from publisher's server
- No redistribution of raw assets
- Third-party notices included per Section 1.2.a
- API costs prominently disclosed per Section 1.5.c

We're open to alternative approaches if this method doesn't meet guidelines.

Testing:
FirstTimeSetup has been tested in clean Unity projects and works reliably.

Thank you for your review!
```

**Why this matters:** Asset Store reviewers see hundreds of submissions. Clear explanation upfront saves review time and shows you've thought through compliance.

---

## Phase 8: Post-Submission

**What happens next:**

### 1. Automated Review (1-2 hours)
- Checks package structure
- Scans for common issues
- Verifies file formats

### 2. Manual Review (2-7 days typically)
- Human reviewer tests package
- Checks compliance
- Verifies functionality

### 3. Possible Outcomes

#### A) Approved ✅
- Package goes live
- You get email notification
- Start beta testing with NB community!

#### B) Requires Changes ⚠️
- Reviewer lists specific issues
- You fix and resubmit
- Common: missing documentation, unclear API costs, etc.

#### C) Rejected (download-on-demand not allowed) ❌
- Fall back to DLL-only implementation
- See `SUBMISSION_STATUS.md` for fallback plan
- Estimated 1-2 days to refactor

---

## Summary Checklist

Track your progress:

- [ ] **Phase 1:** Upload runtime packages to GitHub Release `v1.1.0-runtime-deps`
- [ ] **Phase 2:** Verify all three download URLs return 200/302
- [ ] **Phase 3:** Test FirstTimeSetup in clean Unity project - downloads work
- [ ] **Phase 4:** Mark tests complete in SUBMISSION_STATUS.md
- [ ] **Phase 5:** Commit changes and tag `v1.1.0-beta`
- [ ] **Phase 6:** Export `Synthesis.Pro.unitypackage`
- [ ] **Phase 7:** Submit to Asset Store with cover letter
- [ ] **Phase 8:** Monitor email for review results

---

## Time Estimates

- **Phase 1** (Upload to GitHub): 10 mins
- **Phase 2** (Verify URLs): 2 mins
- **Phase 3** (Test Setup): 15 mins
- **Phase 4** (Update Docs): 2 mins
- **Phase 5** (Git Commit/Tag): 5 mins
- **Phase 6** (Export Package): 3 mins
- **Phase 7** (Submit to Store): 30 mins
- **Phase 8** (Wait for Review): 2-7 days

**Total Active Time: ~1 hour**

---

## What You're Learning

- GitHub Releases for large file hosting
- Unity package distribution workflows
- Asset Store submission process
- Professional software release procedures
- Documentation-driven development
- Download-on-demand architecture
- Compliance with platform guidelines

---

## Reference Files

- `SUBMISSION_STATUS.md` - Compliance checklist
- `UPLOAD_RUNTIME_PACKAGES.md` - GitHub Releases upload guide
- `ASSET_STORE_DESCRIPTION_TEMPLATE.md` - Store listing template
- `COMPLETE_SETUP_CHECKLIST.md` - Full distribution system setup
- `DEVELOPER_LOG.md` - Project tracking

---

**Created:** 2026-02-03
**Session:** Current
**Status:** Ready to execute
**Next Action:** Phase 1 - Upload to GitHub Releases
