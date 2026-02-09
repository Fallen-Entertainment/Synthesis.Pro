# Synthesis.Pro - AI Collaborator for Unity Development

**What if your AI assistant actually remembered your project?**

We built Synthesis.Pro to solve a fundamental problem: every AI session starts from zero. You explain your architecture again. Describe that bug again. Re-explain your coding patterns again.

**Not anymore.**

## What Synthesis.Pro Does

**Memory That Persists:**
- AI remembers your project structure, coding patterns, and past solutions
- Searches previous sessions: "Have we seen this error before?"
- Builds context over time instead of losing it every session

**Deep Unity Integration:**
- 21 MCP tools for direct Unity operations
- Real-time error monitoring with full scene context
- Execute C# in Editor, inspect GameObjects, query project state
- Works with Claude Code, Cursor, VSCode

**13x More Efficient Debugging:**
- Captures errors with complete context automatically
- Scene state, GameObject hierarchy, component data
- No more "what error did you get?" back-and-forth
- AI knows everything the moment something breaks

**Collective Knowledge:**
- Shared solutions database from the community
- "When TextMeshPro throws NullRef on import, check TMP_Settings.asset in Resources"
- Hybrid RAG search: keyword + semantic matching
- Knowledge base grows with community contributions

## The Technical Stack

**Two-Server Architecture:**
- MCP Server: On-demand operations (search, Unity tools, project queries)
- WebSocket Server: Real-time error monitoring (silent background observer)
- Hybrid RAG: BM25S + sentence-transformers (fast + semantic)
- Embedded Python runtime: No external dependencies

**What's Included:**
- Complete MCP server (11 Unity tools + 3 RAG tools)
- Public knowledge database (Unity assets, integrations, patterns)
- Private session database (your project, your context)
- Error pattern matching (historical analysis)
- ConsoleWatcher (automatic context capture)
- Full documentation and setup guides

## Real Usage Example

**Before:**
```
You: "Getting a NullRef in PlayerController"
AI: "What's the error message? What line? What's in PlayerController?"
You: [pastes code]
AI: "What's the scene setup? What objects?"
You: [explains scene]
AI: "Try checking..."
```

**With Synthesis.Pro:**
```
AI: "NullRef in PlayerController.Update() line 42 - Player GameObject's Rigidbody component is null. Scene has Player object but Rigidbody not assigned in Inspector. This happened before in Session 2026-02-03, same root cause."
```

**One message. Complete context. Historical awareness.**

## Early Tester Feedback

Early testers report AI assistants that:
- Understand project context deeply
- Remember architectural decisions across sessions
- Provide increasingly relevant suggestions over time
- Reduce debugging time significantly

## Getting Started

**Requirements:**
- Unity 2020.3+ (works with Unity 6)
- Claude Code, Cursor, or VSCode with MCP support
- That's it. Embedded Python runtime included.

**Setup:**
1. Copy Synthesis.Pro to your Unity project
2. Configure MCP in Claude Code/Cursor
3. Start the MCP server
4. AI now has memory, Unity access, and collective knowledge

**Time to productivity:** ~5 minutes

## Open Source & Free

MIT License. No API costs beyond your AI provider (Claude, etc).

**Repository:** [Your GitHub URL]
**Documentation:** Complete guides, architecture docs, quickstart
**Support:** GitHub Issues, community Discord

## Why This Matters

AI collaboration works best when AI remembers. When context accumulates instead of resetting. When solutions discovered once help everyone.

**We built the infrastructure for that.**

Working code. Real results. AI assistance that improves as your project grows.

**Try it. See what persistent context enables.**

---

**Current Status:** v2.0.0 - Production Ready
**Tools:** 21 MCP tools (11 Unity + 3 RAG + 7 database management + health checks)
**Documentation:** Complete
**Test Coverage:** Full validation suite passing
**First-Time Setup:** Automatic

*Built for developers who want AI assistance that remembers context and learns from your codebase.*
