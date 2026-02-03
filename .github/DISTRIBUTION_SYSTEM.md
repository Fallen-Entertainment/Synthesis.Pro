# Synthesis.Pro Distribution & Update System

Complete automated system for distributing updates and managing user installations.

## Architecture Overview

```
GitHub Repository
├── Source Code (main branch)
├── GitHub Releases
│   └── Synthesis.Pro.unitypackage (v1.x.x)
└── GitHub Pages (gh-pages branch)
    ├── version.json (update manifest)
    ├── downloads/
    │   ├── python-embedded.zip (~50MB)
    │   └── models.zip (~200MB)
    └── api/
        └── sync/ (public DB sync endpoint)
```

## User Journey

### First-Time Installation

1. **User downloads** `Synthesis.Pro.unitypackage` from GitHub Releases
2. **Import into Unity** project
3. **First-time setup runs automatically**:
   - Creates databases (private + public)
   - Downloads Python runtime
   - Downloads AI models
   - Initializes environment
4. **Ready to use!**

### Checking for Updates

1. User opens Unity
2. Clicks `Synthesis > Check for Updates`
3. System checks: `https://fallen-entertainment.github.io/Synthesis.Pro/version.json`
4. If newer version available:
   - Shows changelog
   - Opens download link
5. User imports new package
6. Existing data preserved (databases kept)

### Syncing Public Knowledge

1. User clicks `Synthesis > Data Management > Sync Public Knowledge`
2. **Upload phase**:
   - Compresses public DB
   - Uploads to central server
   - Contributes to community
3. **Download phase**:
   - Downloads community entries
   - Merges into local public DB
4. **User gets latest Unity knowledge from community**

## Files & Their Roles

### Editor Scripts

| File | Purpose |
|------|---------|
| `FirstTimeSetup.cs` | Runs on first import, downloads deps |
| `ExportPackage.cs` | Exports `.unitypackage` for distribution |
| `PublicDBSync.cs` | Syncs public knowledge with community |
| `SynthesisEditorTools.cs` | Update checker, menu items |

### Databases

| Database | Contains | Synced? |
|----------|----------|---------|
| `synthesis_private.db` | Chat archives, user learnings | ❌ Never |
| `synthesis_public.db` | Unity tips, solutions | ✅ Optional |

### Downloads (GitHub Pages)

| File | Size | Purpose |
|------|------|---------|
| `python-embedded.zip` | ~50MB | Embedded Python 3.11 |
| `models.zip` | ~200MB | AI embedding models |
| `version.json` | <1KB | Update manifest |

## Release Process

### For Maintainer (You)

```bash
# 1. Update version
# Edit: Assets/Synthesis.Pro/Editor/SynthesisEditorTools.cs
# Change: CURRENT_VERSION = "1.2.0"

# 2. Commit and tag
git add .
git commit -m "Release v1.2.0: New features..."
git tag v1.2.0
git push origin main
git push origin v1.2.0

# 3. GitHub Actions does the rest!
# - Builds package
# - Creates release
# - Updates version.json
```

### What Happens Automatically

1. **GitHub Actions triggered** by version tag
2. **Unity package exported** via `ExportPackage.cs`
3. **GitHub Release created** with changelog
4. **Package uploaded** to release assets
5. **version.json updated** on GitHub Pages:
   ```json
   {
     "version": "1.2.0",
     "url": "https://github.com/.../releases/download/v1.2.0/Synthesis.Pro.unitypackage",
     "notes": "New features: ..."
   }
   ```

## Data Privacy & Sync

### What's Private (Never Leaves Machine)

- ❌ Chat archives
- ❌ User preferences
- ❌ Personal notes
- ❌ Project-specific data
- ❌ `synthesis_private.db`

### What's Public (Optional Sync)

- ✅ Unity solutions (generic)
- ✅ Best practices
- ✅ Error patterns (anonymized)
- ✅ `synthesis_public.db`

Users can opt-in to sync public knowledge, helping everyone while keeping private data local.

## Server Requirements

### GitHub Pages Hosting

```
gh-pages branch:
├── version.json
├── downloads/
│   ├── python-embedded.zip
│   └── models.zip
└── api/
    └── sync/
        ├── upload (POST endpoint)
        └── download (GET endpoint)
```

### Sync API (Optional)

For public DB sync, you need:

1. **Upload endpoint**: Receives compressed public DBs
2. **Download endpoint**: Sends merged community knowledge
3. **Merge service**: Combines public DBs, deduplicates

Can use:
- GitHub Pages + Cloudflare Workers
- Firebase Functions
- AWS Lambda
- Simple Express.js server

## Bandwidth Considerations

### Per User, First Install:
- Package download: ~5MB
- Python runtime: ~50MB
- AI models: ~200MB
- **Total: ~255MB**

### Per Update:
- Package download: ~5MB
- Version check: <1KB
- Public sync (optional): ~2-10MB

### For 1000 Users:
- Initial: ~255GB
- Updates: ~5GB per version
- Monthly sync: ~5-10GB

**Recommendation**: Use CDN (GitHub Pages + Cloudflare is free)

## Testing the System

### Local Testing

```bash
# 1. Test package export
Unity → Synthesis → Export Package

# 2. Test version check
Unity → Synthesis → Check for Updates

# 3. Test first-time setup
Unity → Synthesis → Setup → Reset Setup
# (Then restart Unity)

# 4. Test sync
Unity → Synthesis → Data Management → Sync Public Knowledge
```

### Pre-Release Checklist

- [ ] Version updated in code
- [ ] Package exports without errors
- [ ] Update checker works
- [ ] First-time setup completes
- [ ] Databases initialize correctly
- [ ] Python runtime accessible
- [ ] Models load successfully
- [ ] Public sync works (if enabled)

## Troubleshooting

### Package Not Building

**Check**:
- Unity license secrets set correctly
- GitHub Actions has permissions
- Export script path correct

**Fix**: Review GitHub Actions logs

### Downloads Failing

**Check**:
- GitHub Pages enabled
- Files uploaded to gh-pages branch
- URLs in code match actual URLs

**Fix**: Verify download URLs in `FirstTimeSetup.cs`

### Sync Not Working

**Check**:
- Sync endpoints responding
- Public DB exists
- Internet connection

**Fix**: Test endpoints manually, check logs

## Future Enhancements

### Planned Features

1. **Delta updates** - Only download changed files
2. **P2P sync** - User-to-user knowledge sharing
3. **Auto-update** - Background updates with notification
4. **Telemetry** - Anonymous usage stats for improvements
5. **Package manager** - In-Unity package browser

### Scalability

If user base grows:
1. Move to CDN (Cloudflare, AWS CloudFront)
2. Implement delta compression
3. Add regional mirrors
4. Use torrent for large files
5. Implement P2P distribution

## Summary

After pushing tags, the entire system is automated:

✅ **Users get**:
- Automatic database setup
- Downloaded dependencies
- Update notifications
- Optional community sync

✅ **You get**:
- Automated releases
- Version tracking
- Usage analytics (opt-in)
- Community contributions

✅ **System provides**:
- Zero-config installation
- Seamless updates
- Privacy-first sync
- Scalable distribution

Everything works together to create a professional, automated distribution system!
