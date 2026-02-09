# Synthesis.Pro Structure Validation System

## Overview

The FirstTimeSetup includes a comprehensive **Structure Validation and Correction** system that automatically ensures your project structure is correct. This system runs:

- **Automatically** on every Unity startup
- **During first-time setup**
- **Manually** via menu: `Tools > Synthesis > Setup > Validate Project Structure`

## What It Does

### 1. Ensures Critical Directories Exist

Creates missing directories:
- `Server/database/` - User databases
- `Server/runtime/` - Runtime-generated files
- `Server/models/` - AI models cache
- `Server/context_systems/` - Context capture systems
- `Server/core/` - Core Python modules
- `RAG/core/` - RAG engine

### 2. Migrates Files from Wrong Locations

**Databases** (synthesis_*.db):
- From project root → `Server/database/`
- From `Server/core/` → `Server/database/` (v1.0 legacy)

**Models cache**:
- From project root → `Server/models/`
- From package root → `Server/models/`
- From `Server/core/models/` → `Server/models/`

**Python runtime**:
- From `Assets/Synthesis.Pro/PythonRuntime/` → project root `PythonRuntime/`
- (Keeps it outside Unity's import system for speed)

### 3. Cleans Up Deprecated Files

Removes:
- `Server/python/` - Old bundled Python location
- `KnowledgeBase/` - Old structure
- `migration_log.txt` - Temporary files

### 4. Reports All Changes

Console output shows:
```
[Synthesis] Validating project structure...
  ✓ Created: Server/runtime
  ✓ Migrated: synthesis_private.db → Server/database/
  ✓ Removed deprecated: python/

[Synthesis] ✅ Structure validated - 3 issue(s) fixed
```

If everything is correct:
```
[Synthesis] ✅ Structure validated - all correct
```

## Use Cases

### First Install
- Creates all required directories
- Sets up clean structure
- No manual intervention needed

### Major Version Updates
- Migrates old structure to new layout
- Removes deprecated files
- Ensures compatibility

### Error Recovery
- User accidentally moved files? Fixed automatically
- Corrupted structure? Rebuilt automatically
- Manual validation available anytime

### Team Collaboration
- Each team member gets correct structure
- No "works on my machine" issues
- Consistent across all installations

## Manual Validation

Run anytime via Unity menu:

**Tools → Synthesis → Setup → Validate Project Structure**

Shows dialog with results. Safe to run repeatedly.

## Version Migration Support

The system is designed to handle migrations between versions:

**Current Version Migrations:**
- v1.0 → v1.1: Moves databases from `core/` to `database/`
- v1.0 → v1.1: Moves Python from Assets to project root
- Any version: Creates missing directories

**Future-Proof:**
Add new migrations by extending `ValidateAndCorrectStructure()`:
```csharp
// In future versions, add:
if (OldStructureExists() && !NewStructureExists())
{
    MigrateToNewStructure();
    report.AppendLine("✓ Migrated to v2.0 structure");
    issuesFixed++;
}
```

## Safety Features

1. **Non-Destructive**: Never deletes files without checking
2. **Preserves Data**: Moves files, doesn't overwrite
3. **Reports Actions**: Shows everything that was changed
4. **Safe Re-runs**: Can run multiple times safely
5. **Error Handling**: Catches and logs exceptions without breaking

## Benefits

- ✅ **Self-Healing**: Automatically fixes structure issues
- ✅ **Update-Friendly**: Handles version migrations automatically
- ✅ **User-Friendly**: No manual file management needed
- ✅ **Team-Friendly**: Consistent structure across installations
- ✅ **Debug-Friendly**: Clear reports of what was fixed

## Technical Details

**Runs At:**
- `EditorApplication.delayCall` on Unity startup
- `FirstTimeSetup.RunSetup()` during setup
- `ManualValidateStructure()` via menu

**Does NOT Run:**
- In Play mode
- During builds
- When Unity is compiling

**Performance:**
- Fast (~100ms typical)
- Only does work when issues found
- Skipped if already validated in session

---

**Result:** Your project structure is always correct, whether it's a fresh install, major update, or someone accidentally moved files around. Just works. 🎯
