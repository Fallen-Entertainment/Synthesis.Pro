# GitHub Pages Setup Guide

**Purpose:** Host runtime downloads for Asset Store package
**URL:** https://fallen-entertainment.github.io/Synthesis.Pro/downloads/
**Required Files:** python-embedded.zip, node-embedded.zip, models.zip

---

## Required Downloads

### 1. Python Embedded Runtime (`python-embedded.zip`)

**Source:**
```
https://www.python.org/ftp/python/3.11.0/python-3.11.0-embed-amd64.zip
```

**What to include:**
- All contents of python-3.11.0-embed-amd64.zip
- All Python packages from `Assets/Synthesis.Pro/KnowledgeBase/python/`
- Structure should match: `/python/python.exe`, `/python/Lib/`, etc.

**How to create:**
1. Download Python embedded from official source
2. Extract to temporary folder
3. Copy all site-packages from your working KnowledgeBase/python/
4. Zip the entire folder as `python-embedded.zip`
5. Test extraction to verify structure

**Approximate size:** ~50MB

---

### 2. Node.js Runtime (`node-embedded.zip`)

**Source:**
```
https://nodejs.org/dist/v18.19.0/node-v18.19.0-win-x64.zip
```

**What to include:**
- `node.exe` from official Node.js distribution
- Any required Node.js dependencies

**How to create:**
1. Download Node.js Windows binary from official source
2. Extract and locate `node.exe`
3. Create zip with structure: `/node.exe`
4. Verify executable works standalone

**Approximate size:** ~20MB

---

### 3. AI Models (`models.zip`)

**Source:** Your trained/downloaded models from `Synthesis.Pro/Server/models/`

**What to include:**
- All ONNX/PyTorch model files
- Model configuration files
- Tokenizers and vocabularies

**How to create:**
1. Zip contents of `Synthesis.Pro/Server/models/`
2. Maintain folder structure if needed
3. Test extraction

**Approximate size:** ~200MB

---

## GitHub Pages Setup Steps

### Option A: Using GitHub Pages Directly

1. **Create downloads branch:**
   ```bash
   git checkout -b gh-pages
   ```

2. **Create downloads directory:**
   ```bash
   mkdir -p downloads
   ```

3. **Add the three zip files:**
   ```bash
   cp python-embedded.zip downloads/
   cp node-embedded.zip downloads/
   cp models.zip downloads/
   ```

4. **Create index.html (optional):**
   ```html
   <!DOCTYPE html>
   <html>
   <head>
       <title>Synthesis.Pro Downloads</title>
   </head>
   <body>
       <h1>Synthesis.Pro Runtime Downloads</h1>
       <ul>
           <li><a href="downloads/python-embedded.zip">Python Runtime</a> (~50MB)</li>
           <li><a href="downloads/node-embedded.zip">Node.js Runtime</a> (~20MB)</li>
           <li><a href="downloads/models.zip">AI Models</a> (~200MB)</li>
       </ul>
       <p>For use with Synthesis.Pro Unity Asset</p>
   </body>
   </html>
   ```

5. **Commit and push:**
   ```bash
   git add downloads/ index.html
   git commit -m "Add runtime downloads for Asset Store package"
   git push origin gh-pages
   ```

6. **Enable GitHub Pages:**
   - Go to repository Settings → Pages
   - Source: gh-pages branch
   - Save

7. **Verify URLs work:**
   - https://fallen-entertainment.github.io/Synthesis.Pro/downloads/python-embedded.zip
   - https://fallen-entertainment.github.io/Synthesis.Pro/downloads/node-embedded.zip
   - https://fallen-entertainment.github.io/Synthesis.Pro/downloads/models.zip

---

### Option B: Using docs/ Folder in Main Branch

1. **Create docs/downloads folder:**
   ```bash
   mkdir -p docs/downloads
   ```

2. **Add zip files:**
   ```bash
   cp python-embedded.zip docs/downloads/
   cp node-embedded.zip docs/downloads/
   cp models.zip docs/downloads/
   ```

3. **Add to .gitattributes for Git LFS (if needed for large files):**
   ```
   docs/downloads/*.zip filter=lfs diff=lfs merge=lfs -text
   ```

4. **Commit and push:**
   ```bash
   git add docs/
   git commit -m "Add runtime downloads"
   git push
   ```

5. **Enable GitHub Pages:**
   - Settings → Pages
   - Source: main branch, /docs folder
   - Save

---

## Testing the Downloads

After hosting, test each URL:

```bash
# Test Python download
curl -I https://fallen-entertainment.github.io/Synthesis.Pro/downloads/python-embedded.zip

# Test Node download
curl -I https://fallen-entertainment.github.io/Synthesis.Pro/downloads/node-embedded.zip

# Test Models download
curl -I https://fallen-entertainment.github.io/Synthesis.Pro/downloads/models.zip
```

Should return `200 OK` for each.

---

## Alternative: Use Releases

Instead of GitHub Pages, you can use GitHub Releases:

1. Create a new release (v1.1.0-runtime-assets)
2. Attach the three zip files as release assets
3. Update FirstTimeSetup.cs URLs to point to release URLs:
   ```
   https://github.com/Fallen-Entertainment/Synthesis.Pro/releases/download/v1.1.0-runtime-assets/python-embedded.zip
   ```

**Pros:**
- No GitHub Pages setup needed
- Built-in download stats
- Version-specific assets

**Cons:**
- URLs are longer
- Tied to specific release versions

---

## Important Notes

1. **File Sizes:**
   - Keep under 2GB (GitHub file size limit)
   - Consider splitting if needed

2. **Bandwidth:**
   - GitHub Pages has soft bandwidth limits
   - Monitor usage if downloads are high

3. **CORS:**
   - GitHub Pages automatically allows cross-origin requests
   - No CORS configuration needed

4. **Update Process:**
   - When runtimes update, replace zip files
   - Commit and push changes
   - URLs stay the same

5. **Security:**
   - Use HTTPS (GitHub Pages enforces this)
   - Consider adding checksums for verification
   - Document exact Python/Node versions

---

## Next Steps After Hosting

1. ✅ Upload all three zip files to GitHub Pages
2. ✅ Test all URLs return 200 OK
3. ✅ Update FirstTimeSetup.cs URLs (already done)
4. ✅ Test FirstTimeSetup in clean Unity project
5. ✅ Export .unitypackage
6. ✅ Submit to Asset Store

---

**Created:** 2026-02-03
**Status:** Ready to implement
**Estimated setup time:** 30 minutes
