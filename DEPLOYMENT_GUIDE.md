# Synthesis.Pro Deployment Guide

## Architecture Change Complete ✅

**What Changed:**
- Python runtime is now **downloaded on first use** (not bundled in repo)
- Keeps git repo small and clean
- Users get ~300MB download during first-time setup
- Industry-standard approach (same as Unity ML-Agents, Barracuda, etc.)

## Setup for Distribution

### 1. Create Python Runtime Zip

**Option A: Manual (Recommended)**
1. Open File Explorer
2. Navigate to: `d:\Unity Projects\Synthesis.Pro\PythonRuntime\`
3. Select all contents inside PythonRuntime/ (the `python` folder and everything else)
4. Right-click → Send to → Compressed (zipped) folder
5. Name it: `python-runtime-v1.0.zip`
6. Move to project root: `d:\Unity Projects\Synthesis.Pro\`

**Option B: PowerShell (if no device files)**
```powershell
cd "d:\Unity Projects\Synthesis.Pro"
# Remove any problematic files first
Remove-Item -Path "PythonRuntime\python\nul" -Force -ErrorAction SilentlyContinue
# Create zip
Compress-Archive -Path "PythonRuntime\*" -DestinationPath "python-runtime-v1.0.zip" -CompressionLevel Optimal
```

**Expected size:** ~300-400MB compressed

### 2. Host on GitHub Releases

1. Go to your Synthesis.Pro GitHub repo
2. Click "Releases" → "Create a new release"
3. Tag: `v1.0.0` (or current version)
4. Title: `Synthesis.Pro v1.0.0`
5. Upload: `python-runtime-v1.0.zip`
6. Publish release

**Result:** Your zip will be available at:
```
https://github.com/YourUsername/Synthesis.Pro/releases/download/v1.0.0/python-runtime-v1.0.zip
```

### 3. Update Download URL in Code

Edit `Assets/Synthesis.Pro/Editor/FirstTimeSetup.cs`:

```csharp
private const string PYTHON_RUNTIME_URL = "https://github.com/YourUsername/Synthesis.Pro/releases/download/v1.0.0/python-runtime-v1.0.zip";
```

Replace `YourUsername` with your actual GitHub username.

### 4. Test the Download Flow

1. Delete your local `PythonRuntime/` folder (backup first!)
2. Restart Unity
3. First-time setup should trigger
4. Should download Python runtime automatically
5. Verify python.exe appears at: `PythonRuntime/python/python.exe`
6. Verify databases initialize correctly

## What Users Will Experience

1. **First Import:**
   - Unity imports the package (~50MB, no Python)
   - First-time setup dialog appears
   - "Download Python runtime? (~300MB)" - one-time download
   - Download happens with progress bar
   - Databases initialize
   - Ready to use!

2. **Subsequent Uses:**
   - PythonRuntime exists - no download needed
   - Only database initialization if needed
   - Fast startup

## Git Status After This Change

**Excluded from repo (in .gitignore):**
- `/PythonRuntime/` - downloaded on first use
- `python-runtime*.zip` - deployment artifact

**Committed to repo:**
- All source code
- All scripts and assets
- Download system in FirstTimeSetup.cs
- Package structure

**Repo size:** ~50-100MB (instead of 800+MB)

## Deployment Checklist

- [ ] Create python-runtime-v1.0.zip
- [ ] Upload to GitHub Releases
- [ ] Update PYTHON_RUNTIME_URL in FirstTimeSetup.cs
- [ ] Test download flow works
- [ ] Commit all code changes
- [ ] Push to GitHub
- [ ] Verify users can clone and import successfully

## Version Updates

When updating Python runtime:
1. Create new zip: `python-runtime-v1.1.zip`
2. Upload as new release
3. Update URL in FirstTimeSetup.cs
4. Increment version tag

## Troubleshooting

**Download fails:**
- Check URL is correct and accessible
- Verify GitHub release is public
- Check file name matches exactly

**Extraction fails:**
- Check zip structure: should contain `/python/` folder at root
- Verify zip isn't corrupted
- Check disk space (~1GB free needed)

**Python not found after download:**
- Check path: `PythonRuntime/python/python.exe`
- Verify zip extracted correctly
- Try manual extraction to test

---

**You're now ready for clean deployment!** 🚀

No more giant repos, no more LFS complexity. Just clean code and on-demand downloads.
