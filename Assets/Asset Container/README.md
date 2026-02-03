# Asset Container

**Working Directory - Not Version Controlled**

## Purpose

This folder serves as a temporary workspace for development and testing assets that should not be tracked by version control or included in distribution packages.

## Use Cases

### 1. **Development Testing**
- Test assets and prototypes
- Experimental features and implementations
- Temporary debugging materials

### 2. **Game-Specific Assets**
- Project-specific implementations that don't belong in the core package
- Custom integrations for your specific Unity project
- Assets that are specific to your game/application

### 3. **Work-in-Progress**
- Assets being developed before committing to the main package
- Incomplete features or experimental code
- Draft documentation and notes

### 4. **Build Artifacts**
- Temporary build outputs
- Generated files during development
- Cache files that don't need version control

## Important Notes

⚠️ **Not Included in Distribution**
- This folder is excluded from `.gitignore`
- It will not be included in the `Synthesis.Pro.unitypackage` export
- Contents are local to your development environment only

✅ **Safe for Personal Use**
- Add any assets you need for development
- No risk of accidentally committing sensitive or project-specific content
- Perfect for testing without cluttering the main package

🗑️ **Can Be Deleted**
- This folder can be safely deleted if not needed
- Unity will recreate it automatically if referenced
- No core Synthesis.Pro functionality depends on this folder

## Examples

### What to Put Here:
```
Asset Container/
├── MyGameIntegration.cs       # Your specific game code
├── TestScripts/               # Testing scripts
├── TemporaryAssets/           # Work-in-progress assets
└── Notes/                     # Development notes
```

### What NOT to Put Here:
- Core Synthesis.Pro code (belongs in `Assets/Synthesis.Pro/`)
- Public knowledge base content
- Anything that should be shared with other users

## Directory Structure

This working directory is separate from the core package structure:

```
Assets/
├── Synthesis.Pro/              # Core package (version controlled)
│   ├── Editor/
│   ├── Runtime/
│   └── Documentation/
└── Asset Container/            # Working directory (not version controlled)
    └── README.md (this file)
```

---

*Part of Synthesis.Pro v1.1.0-beta - AI Collaboration for Unity Development*
