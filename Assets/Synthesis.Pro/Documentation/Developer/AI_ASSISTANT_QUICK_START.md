# 🤖 AI Assistant Quick Start Guide

**READ THIS FIRST when working with AI on Synthesis.Pro**

This guide helps AI assistants (and humans) quickly understand how to work effectively with this project.

---

## 🔑 The Golden Rule

**When you lose context or start a new session:**

1. **Check the Developer Log FIRST** → `.devlog/DEVELOPER_LOG.md`
2. Use capability reminder keywords to access tools
3. Don't guess - verify with search tools

---

## 📖 Developer Log System

**Location:** `Assets/Synthesis.Pro/.devlog/DEVELOPER_LOG.md`

**What it contains:**
- Current work in progress (Feature Backlog)
- Session history with searchable session IDs
- Technical decisions and rationale
- Recently completed work
- AI capability reminders

**When to use it:**
- ✅ Context loss/restoration
- ✅ Starting a new session
- ✅ Understanding project history
- ✅ Finding previous decisions
- ✅ Tracking progress on features

**How to use it:**

```markdown
# Quick navigation:
- Feature Backlog → Current TODOs and in-progress work
- Recently Completed → What was done in previous sessions
- Decision Log → Why we made specific technical choices
- AI Capability Reminders → Keywords that trigger tool awareness
```

---

## 🔑 Capability Reminder Keywords

**These keywords remind AI assistants about available tools and capabilities:**

### Core Capabilities
- **Debug** → Detective mode for systematic troubleshooting
- **Log** → Check developer log for context/history
- **KB/Knowledge** → Query knowledge base system

### Workflow Tools
- **Plan** → Enter planning mode for complex tasks
- **Search/Find** → Use Explore agent for codebase searches
- **Test** → Verification and testing workflows
- **Code** → Coding procedures (see `AI_CODING_PROCEDURES.md`)

### Distribution & Version Control
- **Release/Deploy** → Distribution system docs (`.github/` folder)
- **Commit/Git** → Version control protocols and safety
- **Update** → Version management and update system
- **Sync** → Knowledge sharing and sync system

### Tracking & Organization
- **Todo** → Task tracking with TodoWrite tool
- **Metrics** → Data collection and improvement tracking
- **Context/History** → Session recovery and project history

### Important Guidelines

⚠️ **Keywords are awareness triggers, NOT automatic commands**

- Judge context before using tools
- "I'll log in later" ≠ "check the log"
- "The debug build is ready" ≠ "start debugging"
- Simple tasks don't need complex tools

✅ **Good keyword usage:**
- User: "Can you debug this error?" → Consider detective mode
- User: "What did we do last session?" → Read developer log
- User: "Search for all auth code" → Use Explore agent

❌ **Don't auto-trigger on:**
- User: "The debug settings look good" → Just discussing settings
- User: "I'll check my log later" → Talking about their own logs
- User: "Let's plan our meeting" → Not about code planning

---

## 🚀 Quick Start Workflow

### When Starting a New Session

```markdown
1. Read `.devlog/DEVELOPER_LOG.md` (Feature Backlog section)
2. Check "Recently Completed" for recent session work
3. Review "Next Session" notes for current priorities
4. Ask user what they want to work on
5. Use TodoWrite tool to track progress as you work
```

### When Context is Lost

```markdown
1. READ THE DEV LOG FIRST → `.devlog/DEVELOPER_LOG.md`
2. READ AI OBSERVATIONS → `.ailog/AI_OBSERVATIONS.md`
3. Check Feature Backlog for in-progress work
4. Check Recently Completed for context
5. Look for session IDs to search knowledge base
6. Use Search/Find keywords to locate relevant code
```

### When Working on Code

```markdown
1. Check `AI_CODING_PROCEDURES.md` for coding standards
2. Use Search/Find for open-ended searches
3. Use Plan mode for complex multi-file tasks
4. Use Test workflows to verify changes
5. Update dev log when completing features
```

### When Releasing/Deploying

```markdown
1. Check `.github/` folder for distribution guides
2. Follow RELEASE_GUIDE.md or relevant walkthrough
3. Use Commit/Git keywords to remember safety protocols
4. Update SUBMISSION_STATUS.md if Asset Store related
5. Document the release in dev log
```

---

## 📚 Key Documentation Locations

### Essential Reading (Check These First)
- **Developer Log** → `.devlog/DEVELOPER_LOG.md`
- **AI Coding Procedures** → `Documentation/Developer/AI_CODING_PROCEDURES.md`
- **This Guide** → `Documentation/Developer/AI_ASSISTANT_QUICK_START.md`

### Project-Specific Guides
- **Knowledge Base** → `Documentation/KNOWLEDGE_BASE_GUIDE.md`
- **SynLink Integration** → `Documentation/SYNLINK_INTEGRATION_GUIDE.md`
- **Commands Reference** → `Documentation/COMMANDS_REFERENCE.md`

### Distribution & Release
- **Release Guide** → `.github/RELEASE_GUIDE.md`
- **Complete Setup** → `.github/COMPLETE_SETUP_CHECKLIST.md`
- **Asset Store Submission** → `.github/ASSET_STORE_SUBMISSION_WALKTHROUGH.md`

### Asset Store (If Applicable)
- **Submission Status** → `Documentation/Product/SUBMISSION_STATUS.md`
- **Compliance** → `Documentation/Product/ASSET_STORE_COMPLIANCE.md`
- **Description Template** → `Documentation/Product/ASSET_STORE_DESCRIPTION_TEMPLATE.md`

---

## 🎯 Common Scenarios

### Scenario 1: "I just lost context mid-task"

```markdown
✅ DO THIS:
1. Read developer log Feature Backlog
2. Look for in-progress items
3. Check Recently Completed for session context
4. Ask user where you were

❌ DON'T:
- Guess what you were working on
- Start over from scratch
- Ignore the dev log
```

### Scenario 2: "User asks to debug an error"

```markdown
✅ DO THIS:
1. Read the error message
2. Check relevant code
3. Use detective mode IF investigation gets complex
4. Use Search/Find to locate related code
5. Document solution if non-trivial

❌ DON'T:
- Immediately launch detective mode for simple errors
- Guess without reading code
- Skip searching for related code
```

### Scenario 3: "User wants to plan a new feature"

```markdown
✅ DO THIS:
1. Enter Plan mode for complex features
2. Use Search/Find to understand existing code
3. Check AI_CODING_PROCEDURES for standards
4. Break down into steps
5. Get user approval before implementing

❌ DON'T:
- Start coding without planning
- Skip exploring existing architecture
- Make assumptions about requirements
```

### Scenario 4: "User mentions 'log' or 'debug'"

```markdown
✅ DO THIS:
1. Judge context first
2. Is it relevant to your tools/capabilities?
3. If yes, consider using the tool
4. If no, ignore the keyword

❌ DON'T:
- Auto-trigger on every keyword mention
- Read dev log when user says "I'll log in"
- Start debugging when user says "debug build"
```

---

## 🔄 Session Tracking

**Always update the developer log when:**
- Completing a feature
- Making technical decisions
- Discovering important patterns
- Finishing a significant chunk of work

**Format for session entries:**

```markdown
### YYYY-MM-DD - Session <ID>: Brief Title

**Files Created:**
- path/to/file.cs - Description

**Files Modified:**
- path/to/file.cs - What changed

**Decisions Made:**
- Decision: What was decided
  - Rationale: Why

**Session ID:** `session-id-here` (searchable in private KB)
```

---

## ⚠️ Common Mistakes to Avoid

1. **Not reading the dev log first** → Causes context loss and redundant work
2. **Over-triggering on keywords** → "log in" ≠ "check the log"
3. **Guessing instead of searching** → Use Search/Find to verify
4. **Skipping plan mode for complex tasks** → Leads to poor architecture
5. **Not updating progress** → Use TodoWrite, update dev log
6. **Forgetting safety protocols** → Check git safety rules before commits
7. **Starting work without context** → Always check Feature Backlog first

---

## 🎓 Learning Resources

**For AI Assistants:**
- This guide (you're reading it!)
- Developer Log → Full project context
- AI Coding Procedures → Code standards
- Capability Reminders → Tool awareness

**For Humans:**
- Developer Log Guide → `Documentation/DEVELOPER_LOG_GUIDE.md`
- Knowledge Base Guide → `Documentation/KNOWLEDGE_BASE_GUIDE.md`
- Quick Start → `Documentation/QUICK_START.md`

---

## 🤝 Working With Users

**Communication:**
- Be direct and concise
- Don't over-explain unless asked
- Use markdown for code references: [file.cs:42](path/file.cs#L42)
- Reference docs when relevant

**Task Management:**
- Use TodoWrite for tracking progress
- Mark items complete immediately
- Update dev log for completed work
- Always have exactly ONE in-progress todo

**Code Changes:**
- Read files before modifying
- Follow AI_CODING_PROCEDURES.md
- Use Plan mode for complex changes
- Test changes when appropriate

---

## 📊 Success Metrics

**You're doing well when:**
- ✅ Context restored quickly from dev log
- ✅ Using appropriate tools for each task
- ✅ Updating documentation as you work
- ✅ Following coding procedures
- ✅ Tracking progress with todos
- ✅ Making informed decisions

**Warning signs:**
- ❌ Starting over without checking dev log
- ❌ Guessing instead of searching
- ❌ Breaking coding standards
- ❌ Not tracking progress
- ❌ Over-triggering tools

---

## 🚦 Quick Reference

| Task | Action | Tool/Doc |
|------|--------|----------|
| Lost context | Read dev log | `.devlog/DEVELOPER_LOG.md` |
| Debug error | Check error, use detective mode if complex | Detective mode |
| Search codebase | Use Explore agent | Search/Find keyword |
| Plan feature | Enter plan mode | Plan keyword |
| Check standards | Read coding procedures | `AI_CODING_PROCEDURES.md` |
| Track progress | Use TodoWrite | Todo keyword |
| Commit code | Follow git safety | Commit/Git keyword |
| Release | Follow guides | `.github/` docs |

---

**Remember: The developer log is your friend. Check it first, always.**

**🎯 Next Action:** Read `.devlog/DEVELOPER_LOG.md` → Feature Backlog → Start working!

---

**Created:** 2026-02-04
**Purpose:** Quick start guide for AI assistants working on Synthesis.Pro
**Status:** Living document - update as patterns emerge
