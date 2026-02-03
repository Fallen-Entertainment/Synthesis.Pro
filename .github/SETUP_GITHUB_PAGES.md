# GitHub Pages Setup Guide

Step-by-step guide to set up hosting for downloads and version checking.

## Step 1: Create gh-pages Branch

```bash
# Create orphan branch (no history)
git checkout --orphan gh-pages

# Remove all files
git rm -rf .

# Create directory structure
mkdir -p downloads api/sync

# Create version.json
cat > version.json << 'EOF'
{
  "version": "1.1.0",
  "url": "https://github.com/Fallen-Entertainment/Synthesis.Pro/releases/latest/download/Synthesis.Pro.unitypackage",
  "notes": "Initial release: AI-Unity integration, RAG system, Knowledge base"
}
EOF

# Create index.html (optional landing page)
cat > index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Synthesis.Pro</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
        h1 { color: #333; }
        .version { background: #f0f0f0; padding: 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>Synthesis.Pro - AI Unity Integration</h1>
    <div class="version">
        <h2>Latest Version: <span id="version">Loading...</span></h2>
        <p><a href="" id="download">Download Latest</a></p>
    </div>
    <script>
        fetch('version.json')
            .then(r => r.json())
            .then(data => {
                document.getElementById('version').textContent = data.version;
                document.getElementById('download').href = data.url;
            });
    </script>
</body>
</html>
EOF

# Commit
git add .
git commit -m "Initial GitHub Pages setup"
git push origin gh-pages

# Switch back to main
git checkout main
```

## Step 2: Enable GitHub Pages

1. Go to: **Settings > Pages**
2. Source: **Deploy from a branch**
3. Branch: **gh-pages** / (root)
4. Click **Save**

Wait a few minutes, then visit:
`https://fallen-entertainment.github.io/Synthesis.Pro/`

## Step 3: Prepare Python Embedded Runtime

### Download Official Python Embedded

```bash
# Download Python 3.11 embedded (Windows x64)
curl -O https://www.python.org/ftp/python/3.11.8/python-3.11.8-embed-amd64.zip

# Extract and test
unzip python-3.11.8-embed-amd64.zip -d python-embedded
cd python-embedded

# Install pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
./python.exe get-pip.py

# Install required packages
./python.exe -m pip install sqlite-rag sentence-transformers chromadb

# Create requirements.txt for users
cat > requirements.txt << 'EOF'
sqlite-rag>=0.1.0
sentence-transformers>=2.2.0
chromadb>=0.4.0
numpy>=1.24.0
EOF

cd ..

# Zip it up
zip -r python-embedded.zip python-embedded/

# Check size (should be ~50MB)
ls -lh python-embedded.zip
```

## Step 4: Prepare AI Models

```bash
# Create models directory
mkdir models

# Download embedding model (EmbeddingGEMMA 300M)
cat > download_models.py << 'EOF'
from sentence_transformers import SentenceTransformer

# Download model (will be cached)
model = SentenceTransformer('all-MiniLM-L6-v2')  # Small, fast model

# Save to models directory
model.save('models/embedding-model')

print("✅ Model downloaded to models/")
EOF

python download_models.py

# Zip models
zip -r models.zip models/

# Check size (should be ~100-200MB)
ls -lh models.zip
```

## Step 5: Upload to GitHub Pages

### Option A: Manual Upload (Easy)

1. Go to your gh-pages branch on GitHub
2. Click **Add file > Upload files**
3. Upload `python-embedded.zip` to `downloads/` folder
4. Upload `models.zip` to `downloads/` folder
5. Commit changes

### Option B: Git Push (Recommended)

```bash
# Switch to gh-pages branch
git checkout gh-pages

# Create downloads directory
mkdir -p downloads

# Copy files
cp python-embedded.zip downloads/
cp models.zip downloads/

# Check gitignore doesn't block large files
# (GitHub has 100MB file limit, use Git LFS for larger files)

# If files are too large, use Git LFS
git lfs install
git lfs track "downloads/*.zip"
git add .gitattributes

# Add and commit
git add downloads/
git commit -m "Add Python runtime and AI models"

# Push (may take a while for large files)
git push origin gh-pages

# Switch back to main
git checkout main
```

### Option C: Use Release Assets Instead

If files are too large for GitHub Pages:

```bash
# Create a release for downloads
gh release create v1.0.0-deps \
  python-embedded.zip \
  models.zip \
  --title "Dependencies v1.0.0" \
  --notes "Embedded Python runtime and AI models"

# Update URLs in FirstTimeSetup.cs to point to:
# https://github.com/Fallen-Entertainment/Synthesis.Pro/releases/download/v1.0.0-deps/python-embedded.zip
```

## Step 6: Update Download URLs

Edit `Assets/Synthesis.Pro/Editor/FirstTimeSetup.cs`:

```csharp
// Update these URLs:
private const string PYTHON_DOWNLOAD_URL = "https://fallen-entertainment.github.io/Synthesis.Pro/downloads/python-embedded.zip";
private const string MODELS_DOWNLOAD_URL = "https://fallen-entertainment.github.io/Synthesis.Pro/downloads/models.zip";

// OR if using release assets:
private const string PYTHON_DOWNLOAD_URL = "https://github.com/Fallen-Entertainment/Synthesis.Pro/releases/download/v1.0.0-deps/python-embedded.zip";
private const string MODELS_DOWNLOAD_URL = "https://github.com/Fallen-Entertainment/Synthesis.Pro/releases/download/v1.0.0-deps/models.zip";
```

## Step 7: Test Downloads

```bash
# Test version.json
curl https://fallen-entertainment.github.io/Synthesis.Pro/version.json

# Test Python download
curl -I https://fallen-entertainment.github.io/Synthesis.Pro/downloads/python-embedded.zip

# Test models download
curl -I https://fallen-entertainment.github.io/Synthesis.Pro/downloads/models.zip
```

## Step 8: Create Sync API (Optional)

### Simple Cloudflare Worker

Create `api/sync/index.js` in gh-pages:

```javascript
export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // CORS headers
    const headers = {
      'Access-Control-Allow-Origin': '*',
      'Content-Type': 'application/json'
    };

    // Upload endpoint
    if (url.pathname === '/api/sync/upload' && request.method === 'POST') {
      // Store uploaded public DB
      const data = await request.arrayBuffer();

      // Save to KV storage or R2
      await env.PUBLIC_DBS.put(
        `db_${Date.now()}.gz`,
        data,
        { metadata: { timestamp: Date.now() } }
      );

      return new Response(JSON.stringify({ success: true }), { headers });
    }

    // Download endpoint
    if (url.pathname === '/api/sync/download' && request.method === 'GET') {
      // Get merged community DB
      const mergedDb = await env.PUBLIC_DBS.get('merged_public.db.gz');

      if (!mergedDb) {
        return new Response('Not found', { status: 404 });
      }

      return new Response(mergedDb, {
        headers: {
          'Content-Type': 'application/gzip',
          'Access-Control-Allow-Origin': '*'
        }
      });
    }

    return new Response('Not found', { status: 404 });
  }
};
```

Deploy to Cloudflare Workers:

```bash
npm install -g wrangler
wrangler init synthesis-sync
# Copy index.js above
wrangler deploy
```

**OR skip sync API for now** - it's optional!

## Verification Checklist

- [ ] gh-pages branch exists
- [ ] GitHub Pages enabled and accessible
- [ ] version.json accessible at `/version.json`
- [ ] python-embedded.zip accessible (or via release)
- [ ] models.zip accessible (or via release)
- [ ] URLs in code match actual URLs
- [ ] Test download in Unity

## Summary

You now have:
- ✅ GitHub Pages site
- ✅ Version checking endpoint
- ✅ Python runtime download
- ✅ AI models download
- ✅ (Optional) Sync API

Next: Set up Unity secrets for automated builds!
