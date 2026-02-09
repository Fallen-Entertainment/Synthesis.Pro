using System.IO;
using UnityEngine;

namespace Synthesis.Pro
{
    /// <summary>
    /// Centralized path configuration for Synthesis.Pro
    /// Single source of truth - buttery and creamy, no hard-coding
    /// </summary>
    public static class SynthesisPaths
    {
        // Base directories
        private static string _serverPath = null;
        public static string Server
        {
            get
            {
                if (_serverPath == null)
                {
                    _serverPath = Path.Combine(
                        Application.dataPath,
                        "Synthesis.Pro",
                        "Server"
                    );
                }
                return _serverPath;
            }
        }

        public static string Core => Path.Combine(Server, "core");
        public static string Database => Path.Combine(Server, "database");
        public static string Runtime => Path.Combine(Server, "runtime");
        public static string Models => Path.Combine(Server, "models");
        public static string ContextSystems => Path.Combine(Server, "context_systems");
        public static string RAGIntegration => Path.Combine(Server, "rag_integration");

        // Runtime files (session-specific, current state)
        public static string ConsoleErrors => Path.Combine(Runtime, "console_errors_latest.json");
        public static string AIObservations => Path.Combine(Runtime, "ai_observations.txt");
        public static string SessionState => Path.Combine(Runtime, "session_state.json");

        // Database files
        public static string DbPrivate => Path.Combine(Database, "synthesis_private.db");
        public static string DbKnowledge => Path.Combine(Database, "synthesis_knowledge.db");
        public static string DbPublic => Path.Combine(Database, "synthesis_public.db");

        // Model files
        public static string EmbeddingModel => Path.Combine(Models, "models--sentence-transformers--all-MiniLM-L6-v2");

        /// <summary>
        /// Ensure runtime directory exists - called on startup
        /// </summary>
        public static void EnsureRuntimeExists()
        {
            if (!Directory.Exists(Runtime))
            {
                Directory.CreateDirectory(Runtime);
            }
        }

        /// <summary>
        /// Get path to a session-specific file in runtime/
        /// </summary>
        public static string GetSessionFile(string filename)
        {
            return Path.Combine(Runtime, filename);
        }
    }
}
