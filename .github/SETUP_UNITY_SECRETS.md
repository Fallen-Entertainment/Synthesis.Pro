# Unity GitHub Secrets Setup

Guide to set up Unity credentials for automated builds.

## What You Need

GitHub Actions needs Unity credentials to build your package. You'll create 3 secrets:

1. `UNITY_LICENSE` - Your Unity license file
2. `UNITY_EMAIL` - Your Unity account email
3. `UNITY_PASSWORD` - Your Unity account password

## Option 1: Personal License (Free/Plus/Pro)

### Step 1: Generate License Request File

```bash
# Run Unity in batch mode to generate activation request
"C:\Program Files\Unity\Hub\Editor\<VERSION>\Editor\Unity.exe" ^
  -batchmode ^
  -createManualActivationFile ^
  -quit

# This creates: Unity_v<VERSION>.alf in your project folder
```

### Step 2: Get License File

1. Go to: https://license.unity3d.com/manual
2. Upload the `.alf` file you generated
3. Follow prompts to activate
4. Download the `.ulf` license file

### Step 3: Add Secrets to GitHub

1. Go to your repo: https://github.com/Fallen-Entertainment/Synthesis.Pro
2. Click: **Settings > Secrets and variables > Actions**
3. Click: **New repository secret**

Add these 3 secrets:

#### Secret 1: UNITY_LICENSE

```
Name: UNITY_LICENSE
Value: <paste entire contents of .ulf file>
```

**To get .ulf content:**
```bash
# On Windows
type Unity_v2022_x.x.x.ulf

# On Mac/Linux
cat Unity_v2022_x.x.x.ulf
```

Copy ALL the XML content (including `<?xml` and `</root>`).

#### Secret 2: UNITY_EMAIL

```
Name: UNITY_EMAIL
Value: your.unity.account@email.com
```

#### Secret 3: UNITY_PASSWORD

```
Name: UNITY_PASSWORD
Value: your_unity_password
```

## Option 2: Unity Plus/Pro License

If you have Plus or Pro, same process as above.

## Option 3: No Unity License Yet

### Use Unity Personal (Free)

1. Create Unity account: https://id.unity.com/
2. Download Unity Hub
3. Install Unity 2022.3 LTS or later
4. Activate Personal license in Hub
5. Follow "Option 1" above to get license file

## Testing Your Setup

### Local Test

1. Create a test workflow:

```yaml
# .github/workflows/test-unity.yml
name: Test Unity License
on: workflow_dispatch

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Test Unity License
        uses: game-ci/unity-builder@v4
        env:
          UNITY_LICENSE: ${{ secrets.UNITY_LICENSE }}
          UNITY_EMAIL: ${{ secrets.UNITY_EMAIL }}
          UNITY_PASSWORD: ${{ secrets.UNITY_PASSWORD }}
        with:
          targetPlatform: StandaloneWindows64
```

2. Push to GitHub
3. Go to **Actions > Test Unity License**
4. Click **Run workflow**
5. Check if it succeeds

### Troubleshooting

**Build fails with "Invalid credentials"**
- Double-check email/password
- Make sure license file is complete (starts with `<?xml`)
- Verify license isn't expired

**Build fails with "License not activated"**
- Make sure you activated the .alf file
- Download fresh .ulf from Unity website
- Copy entire file contents to secret

**Build takes too long / times out**
- Normal for first run (downloads Unity)
- Subsequent builds are cached and faster

## Alternative: Unity Build Server

For teams or heavy use:

1. Set up Unity Build Server
2. Use Build Server license instead
3. More info: https://unity.com/products/unity-build-server

## Security Notes

### Protecting Your Secrets

✅ **DO:**
- Use GitHub repository secrets
- Keep secrets private
- Rotate passwords periodically
- Use read-only credentials if possible

❌ **DON'T:**
- Commit secrets to code
- Share secrets publicly
- Use production passwords
- Store secrets in workflow files

### Secret Scope

Repository secrets are:
- ✅ Encrypted at rest
- ✅ Only accessible during workflow runs
- ✅ Not visible in logs
- ✅ Masked in output

## Verification Checklist

After setup, verify:

- [ ] All 3 secrets added to GitHub
- [ ] UNITY_LICENSE contains full XML
- [ ] UNITY_EMAIL is correct
- [ ] UNITY_PASSWORD is correct
- [ ] Test workflow runs successfully
- [ ] Build completes without errors

## What Happens Next

Once secrets are set up:

1. **Push a version tag** (e.g., `v1.1.0`)
2. **GitHub Actions triggers** automatically
3. **Unity builds package** using your license
4. **Package uploaded** to GitHub Releases
5. **version.json updated** on GitHub Pages

All automatic!

## Getting Your License File (Detailed)

If you're having trouble, here's a step-by-step walkthrough:

### Windows

```powershell
# 1. Find your Unity installation
$unityPath = "C:\Program Files\Unity\Hub\Editor\2022.3.0f1\Editor\Unity.exe"

# 2. Generate activation file
& $unityPath -batchmode -createManualActivationFile -quit

# 3. Find the .alf file
Get-ChildItem -Filter "Unity_*.alf"

# 4. Upload to Unity (manually)
# Visit: https://license.unity3d.com/manual

# 5. After downloading .ulf, read it
Get-Content Unity_v*.ulf | Set-Clipboard
Write-Host "License copied to clipboard! Paste into GitHub secret."
```

### Mac

```bash
# 1. Find Unity installation
UNITY="/Applications/Unity/Hub/Editor/2022.3.0f1/Unity.app/Contents/MacOS/Unity"

# 2. Generate activation file
$UNITY -batchmode -createManualActivationFile -quit

# 3. Find the .alf file
ls Unity_*.alf

# 4. Upload to Unity (manually)
# Visit: https://license.unity3d.com/manual

# 5. After downloading .ulf, copy it
cat Unity_v*.ulf | pbcopy
echo "License copied to clipboard! Paste into GitHub secret."
```

### Linux

```bash
# 1. Find Unity installation
UNITY="$HOME/Unity/Hub/Editor/2022.3.0f1/Editor/Unity"

# 2. Generate activation file
$UNITY -batchmode -createManualActivationFile -quit

# 3. Find the .alf file
ls Unity_*.alf

# 4. Upload to Unity (manually)
# Visit: https://license.unity3d.com/manual

# 5. After downloading .ulf, copy it
cat Unity_v*.ulf | xclip -selection clipboard
echo "License copied to clipboard! Paste into GitHub secret."
```

## Common Issues

### "Unity not found"

Make sure Unity is installed:
- Unity Hub: https://unity.com/download
- Install Unity 2022.3 LTS (recommended)

### "Cannot generate .alf file"

Try:
```bash
# Add -logFile flag to see errors
Unity.exe -batchmode -createManualActivationFile -logFile activation.log -quit

# Check log
cat activation.log
```

### "License activation failed"

- Check license type (Personal/Plus/Pro)
- Verify not used on too many machines
- Contact Unity support if needed

## Summary

After completing this guide:

✅ Unity license ready for CI/CD
✅ Secrets secured in GitHub
✅ Automated builds enabled
✅ Ready to release!

Next step: Push your first release tag! 🚀
