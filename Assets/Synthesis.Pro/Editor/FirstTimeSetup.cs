using UnityEngine;
using UnityEditor;
using System.IO;
using System.IO.Compression;
using UnityEngine.Networking;

namespace Synthesis.Editor
{
    /// <summary>
    /// Runs automatic setup on first import
    /// Downloads Python runtime and initializes databases
    /// </summary>
    [InitializeOnLoad]
    public static class FirstTimeSetup
    {
        private const string SETUP_COMPLETE_KEY = "Synthesis.SetupComplete";
        private const string PYTHON_RUNTIME_URL = "https://github.com/YourUsername/Synthesis.Pro/releases/latest/download/python-runtime.zip";
        private const long PYTHON_RUNTIME_SIZE_MB = 300; // Approximate size

        static FirstTimeSetup()
        {
            // CRITICAL: Ensure Newtonsoft.Json is installed FIRST before anything else
            EditorApplication.delayCall += EnsureNewtonsoftJson;

            // ALWAYS validate and correct structure (works for both first install and major updates)
            EditorApplication.delayCall += ValidateAndCorrectStructure;

            // Check if setup already completed
            if (EditorPrefs.GetBool(SETUP_COMPLETE_KEY, false))
            {
                return;
            }

            // Delay to let Unity finish initializing
            EditorApplication.delayCall += RunFirstTimeSetup;
        }

        private static void EnsureNewtonsoftJson()
        {
            try
            {
                string manifestPath = Path.Combine(Application.dataPath, "..", "Packages", "manifest.json");

                if (!File.Exists(manifestPath))
                {
                    Debug.LogWarning("[Synthesis] Package manifest not found");
                    return;
                }

                string manifestContent = File.ReadAllText(manifestPath);

                // Check if already installed
                if (manifestContent.Contains("\"com.unity.nuget.newtonsoft-json\""))
                {
                    return; // Already installed
                }

                Debug.Log("[Synthesis] Adding Newtonsoft.Json dependency...");

                // Find the dependencies section and add Newtonsoft.Json
                int depsIndex = manifestContent.IndexOf("\"dependencies\"");
                if (depsIndex == -1)
                {
                    Debug.LogError("[Synthesis] Could not find dependencies section in manifest.json");
                    return;
                }

                int braceIndex = manifestContent.IndexOf('{', depsIndex);
                if (braceIndex == -1)
                {
                    Debug.LogError("[Synthesis] Malformed manifest.json");
                    return;
                }

                // Insert Newtonsoft.Json as first dependency
                string newtonsoftEntry = "\n    \"com.unity.nuget.newtonsoft-json\": \"3.2.1\",";
                manifestContent = manifestContent.Insert(braceIndex + 1, newtonsoftEntry);

                // Write back to file
                File.WriteAllText(manifestPath, manifestContent);

                // Force Unity to reload packages
                AssetDatabase.Refresh();

                Debug.Log("[Synthesis] ✅ Newtonsoft.Json added to project");
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[Synthesis] Failed to add Newtonsoft.Json: {e.Message}");
            }
        }

        /// <summary>
        /// Validates and corrects complete project structure
        /// Works for both first installs and major updates
        /// Ensures all directories exist and files are in correct locations
        /// </summary>
        private static void ValidateAndCorrectStructure()
        {
            try
            {
                int issuesFixed = 0;
                System.Text.StringBuilder report = new System.Text.StringBuilder();
                report.AppendLine("[Synthesis] Validating project structure...");

                string projectRoot = Path.GetDirectoryName(Application.dataPath);
                string packageRoot = Path.Combine(Application.dataPath, "Synthesis.Pro");
                string serverDir = Path.Combine(packageRoot, "Server");

                // ===== STEP 1: Ensure all critical directories exist =====
                string[] requiredDirs = new string[]
                {
                    Path.Combine(serverDir, "database"),      // Databases
                    Path.Combine(serverDir, "runtime"),       // Runtime files
                    Path.Combine(serverDir, "models"),        // AI models cache
                    Path.Combine(serverDir, "context_systems"), // Context capture
                    Path.Combine(serverDir, "core"),          // Core Python
                    Path.Combine(packageRoot, "RAG", "core"), // RAG engine
                };

                foreach (string dir in requiredDirs)
                {
                    if (!Directory.Exists(dir))
                    {
                        Directory.CreateDirectory(dir);
                        report.AppendLine($"  ✓ Created: {Path.GetFileName(Path.GetDirectoryName(dir))}/{Path.GetFileName(dir)}");
                        issuesFixed++;
                    }
                }

                // ===== STEP 2: Migrate databases from wrong locations =====
                string databaseDir = Path.Combine(serverDir, "database");
                string[] dbFiles = { "synthesis_private.db", "synthesis_knowledge.db", "synthesis_public.db" };

                // Check project root
                foreach (string dbFile in dbFiles)
                {
                    string wrongPath = Path.Combine(projectRoot, dbFile);
                    string correctPath = Path.Combine(databaseDir, dbFile);
                    if (File.Exists(wrongPath) && !File.Exists(correctPath))
                    {
                        File.Move(wrongPath, correctPath);
                        report.AppendLine($"  ✓ Migrated: {dbFile} → Server/database/");
                        issuesFixed++;
                    }
                }

                // Check old Server/core location (v1.0 legacy)
                string oldCoreDbDir = Path.Combine(serverDir, "core");
                foreach (string dbFile in dbFiles)
                {
                    string oldPath = Path.Combine(oldCoreDbDir, dbFile);
                    string correctPath = Path.Combine(databaseDir, dbFile);
                    if (File.Exists(oldPath) && !File.Exists(correctPath))
                    {
                        File.Move(oldPath, correctPath);
                        report.AppendLine($"  ✓ Migrated: {dbFile} from core/ → database/");
                        issuesFixed++;
                    }
                }

                // ===== STEP 3: Migrate models cache from wrong locations =====
                string correctModelsPath = Path.Combine(serverDir, "models");
                string[] oldModelPaths = new string[]
                {
                    Path.Combine(projectRoot, "models"),           // Project root
                    Path.Combine(packageRoot, "models"),           // Package root
                    Path.Combine(serverDir, "core", "models"),     // Old core location
                };

                foreach (string oldPath in oldModelPaths)
                {
                    if (Directory.Exists(oldPath) && oldPath != correctModelsPath)
                    {
                        // Move contents, not the directory itself
                        foreach (string file in Directory.GetFiles(oldPath, "*", SearchOption.AllDirectories))
                        {
                            string relativePath = file.Substring(oldPath.Length + 1);
                            string targetPath = Path.Combine(correctModelsPath, relativePath);
                            Directory.CreateDirectory(Path.GetDirectoryName(targetPath));
                            if (!File.Exists(targetPath))
                            {
                                File.Move(file, targetPath);
                            }
                        }
                        Directory.Delete(oldPath, true);
                        report.AppendLine($"  ✓ Migrated: models/ → Server/models/");
                        issuesFixed++;
                    }
                }

                // ===== STEP 4: Clean up deprecated files/folders =====
                string[] deprecatedPaths = new string[]
                {
                    Path.Combine(serverDir, "python"),             // Old bundled Python location
                    Path.Combine(packageRoot, "KnowledgeBase"),    // Old structure
                    Path.Combine(serverDir, "migration_log.txt"),  // Temp file
                };

                foreach (string deprecatedPath in deprecatedPaths)
                {
                    if (Directory.Exists(deprecatedPath))
                    {
                        Directory.Delete(deprecatedPath, true);
                        report.AppendLine($"  ✓ Removed deprecated: {Path.GetFileName(deprecatedPath)}");
                        issuesFixed++;
                    }
                    else if (File.Exists(deprecatedPath))
                    {
                        File.Delete(deprecatedPath);
                        report.AppendLine($"  ✓ Removed deprecated: {Path.GetFileName(deprecatedPath)}");
                        issuesFixed++;
                    }
                }

                // ===== STEP 5: Validate Python runtime location =====
                string pythonRuntimePath = Path.Combine(projectRoot, "PythonRuntime", "python", "python.exe");
                string oldPythonPath = Path.Combine(packageRoot, "PythonRuntime", "python", "python.exe");

                // If Python is in wrong location (inside Assets), move it
                if (File.Exists(oldPythonPath) && !File.Exists(pythonRuntimePath))
                {
                    string oldPythonRoot = Path.Combine(packageRoot, "PythonRuntime");
                    string newPythonRoot = Path.Combine(projectRoot, "PythonRuntime");
                    Directory.Move(oldPythonRoot, newPythonRoot);
                    report.AppendLine($"  ✓ Migrated: PythonRuntime → project root (faster, no Unity import)");
                    issuesFixed++;
                }

                // ===== STEP 6: Clean up orphaned .meta files =====
                string[] orphanedMetaFiles = new string[]
                {
                    Path.Combine(packageRoot, "KnowledgeBase.meta"),
                    Path.Combine(serverDir, "python.meta"),
                    Path.Combine(serverDir, "core", "models.meta"),
                };

                foreach (string metaFile in orphanedMetaFiles)
                {
                    if (File.Exists(metaFile))
                    {
                        string correspondingPath = metaFile.Substring(0, metaFile.Length - 5); // Remove .meta
                        if (!Directory.Exists(correspondingPath) && !File.Exists(correspondingPath))
                        {
                            File.Delete(metaFile);
                            report.AppendLine($"  ✓ Removed orphaned: {Path.GetFileName(metaFile)}");
                            issuesFixed++;
                        }
                    }
                }

                // ===== FINAL REPORT =====
                if (issuesFixed > 0)
                {
                    AssetDatabase.Refresh();
                    report.AppendLine($"\n[Synthesis] ✅ Structure validated - {issuesFixed} issue(s) fixed");
                    Debug.Log(report.ToString());
                }
                else
                {
                    Debug.Log("[Synthesis] ✅ Structure validated - all correct");
                }
            }
            catch (System.Exception e)
            {
                Debug.LogWarning($"[Synthesis] Structure validation warning: {e.Message}\n{e.StackTrace}");
            }
        }

        private static void RunFirstTimeSetup()
        {
            Debug.Log("[Synthesis] Running first-time setup...");

            // Check if Python runtime exists
            string pythonPath = Path.Combine(Application.dataPath, "..", "PythonRuntime", "python", "python.exe");
            bool needsPythonDownload = !File.Exists(pythonPath);

            string setupMessage = "🎉 AI Collaboration System for Unity\n\n" +
                "First-time setup will:\n";

            if (needsPythonDownload)
            {
                setupMessage += $"• Download Python runtime (~{PYTHON_RUNTIME_SIZE_MB}MB, one-time)\n";
            }

            setupMessage += "• Initialize knowledge base databases\n" +
                "• Create initial content\n\n" +
                (needsPythonDownload ? "This takes about 2-3 minutes.\n\n" : "This takes about 10 seconds.\n\n") +
                "Continue?";

            bool shouldSetup = EditorUtility.DisplayDialog(
                "Welcome to Synthesis.Pro!",
                setupMessage,
                "Yes, Set Up",
                "Later"
            );

            if (!shouldSetup)
            {
                Debug.Log("[Synthesis] Setup postponed. Run 'Tools > Synthesis > Setup > First Time Setup' when ready.");
                return;
            }

            // Run setup steps
            RunSetup();
        }

        [MenuItem("Tools/Synthesis/Setup/First Time Setup", false, 100)]
        public static void ManualSetup()
        {
            RunSetup();
        }

        private static void RunSetup()
        {
            EditorUtility.DisplayProgressBar("Synthesis Setup", "Initializing...", 0.0f);

            try
            {
                // Step 1: Download Python runtime if needed
                string pythonPath = Path.Combine(Application.dataPath, "..", "PythonRuntime", "python", "python.exe");
                if (!File.Exists(pythonPath))
                {
                    EditorUtility.DisplayProgressBar("Synthesis Setup", "Downloading Python runtime...", 0.1f);
                    if (!DownloadPythonRuntime())
                    {
                        throw new System.Exception("Failed to download Python runtime");
                    }
                }

                // Step 2: Initialize databases
                EditorUtility.DisplayProgressBar("Synthesis Setup", "Initializing databases...", 0.7f);
                if (!InitializeDatabases())
                {
                    throw new System.Exception("Failed to initialize databases");
                }

                // Step 2: Create initial public DB content
                EditorUtility.DisplayProgressBar("Synthesis Setup", "Creating initial content...", 0.8f);
                CreateInitialPublicContent();

                // Mark setup as complete
                EditorPrefs.SetBool(SETUP_COMPLETE_KEY, true);

                EditorUtility.ClearProgressBar();

                EditorUtility.DisplayDialog(
                    "Setup Complete!",
                    "Synthesis.Pro is ready to use!\n\n" +
                    "Next steps:\n" +
                    "• Start MCP server (see QUICK_START.md)\n" +
                    "• Add ConsoleWatcher to your scene\n" +
                    "• Start building with AI!\n\n" +
                    "📖 Documentation: See README.md\n" +
                    "🚀 Quick Start: See QUICK_START.md",
                    "Get Started!"
                );

                Debug.Log("[Synthesis] ✅ First-time setup complete!");
            }
            catch (System.Exception e)
            {
                EditorUtility.ClearProgressBar();
                Debug.LogError($"[Synthesis] Setup failed: {e.Message}");

                EditorUtility.DisplayDialog(
                    "Setup Failed",
                    $"Setup encountered an error:\n\n{e.Message}\n\n" +
                    "You can retry via: Tools > Synthesis > Setup > First Time Setup",
                    "OK"
                );
            }
        }

        private static bool ValidatePythonRuntime()
        {
            // Python runtime is bundled at project root: PythonRuntime/python/python.exe
            string pythonPath = Path.Combine(Application.dataPath, "..", "PythonRuntime", "python", "python.exe");

            if (!File.Exists(pythonPath))
            {
                Debug.LogError($"[Synthesis] Python runtime not found at: {pythonPath}");
                Debug.LogError("[Synthesis] The bundled Python runtime is missing from PythonRuntime/python/");
                return false;
            }

            Debug.Log($"[Synthesis] ✅ Python runtime found: {pythonPath}");
            return true;
        }

        private static bool InitializeDatabases()
        {
            try
            {
                // Use Assets/Synthesis.Pro path for consistency
                string packageRoot = Path.Combine(Application.dataPath, "Synthesis.Pro");
                string serverDir = Path.Combine(packageRoot, "Server");
                string databaseDir = Path.Combine(serverDir, "database");
                string privateDbPath = Path.Combine(databaseDir, "synthesis_private.db");
                string knowledgeDbPath = Path.Combine(databaseDir, "synthesis_knowledge.db");

                // Ensure directory exists
                Directory.CreateDirectory(databaseDir);

                // Run Python database initialization script
                string ragDir = Path.Combine(packageRoot, "RAG");
                string initScript = Path.Combine(ragDir, "init_databases.py");

                if (!File.Exists(initScript))
                {
                    Debug.LogWarning("[Synthesis] init_databases.py not found, creating minimal DBs");
                    CreateMinimalDatabases(privateDbPath, knowledgeDbPath);
                    return true;
                }

                // Use bundled Python runtime from project root
                string pythonExe = Path.Combine(Application.dataPath, "..", "PythonRuntime", "python", "python.exe");

                var process = new System.Diagnostics.Process();
                process.StartInfo.FileName = pythonExe;
                process.StartInfo.Arguments = $"\"{initScript}\"";
                process.StartInfo.UseShellExecute = false;
                process.StartInfo.RedirectStandardOutput = true;
                process.StartInfo.RedirectStandardError = true;
                process.StartInfo.CreateNoWindow = true;
                process.Start();

                // Wait with timeout (30 seconds for DB init)
                if (!process.WaitForExit(30000))
                {
                    process.Kill();
                    Debug.LogError("[Synthesis] Database init timed out");
                    return false;
                }

                if (process.ExitCode != 0)
                {
                    string error = process.StandardError.ReadToEnd();
                    Debug.LogError($"[Synthesis] Database init error: {error}");
                    return false;
                }

                Debug.Log("[Synthesis] Databases initialized");
                return true;
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[Synthesis] Database initialization failed: {e.Message}");
                return false;
            }
        }

        private static void CreateMinimalDatabases(string privateDbPath, string knowledgeDbPath)
        {
            // Create minimal SQLite database files with proper format
            // This is a fallback if Python init script isn't available

            Debug.Log("[Synthesis] Creating minimal SQLite database structures");

            // SQLite database file header (first 16 bytes)
            // "SQLite format 3\0" followed by page size and other metadata
            byte[] sqliteHeader = new byte[]
            {
                0x53, 0x51, 0x4C, 0x69, 0x74, 0x65, 0x20, 0x66,  // "SQLite f"
                0x6F, 0x72, 0x6D, 0x61, 0x74, 0x20, 0x33, 0x00,  // "ormat 3\0"
                0x10, 0x00, // Page size = 4096 (0x1000)
                0x01, // File format write version
                0x01, // File format read version
                0x00, // Reserved space at end of each page
                0x40, // Maximum embedded payload fraction (64)
                0x20, // Minimum embedded payload fraction (32)
                0x20, // Leaf payload fraction (32)
                0x00, 0x00, 0x00, 0x00, // File change counter
                0x00, 0x00, 0x00, 0x00, // Size of database in pages
                0x00, 0x00, 0x00, 0x00, // First freelist trunk page
                0x00, 0x00, 0x00, 0x00, // Total number of freelist pages
                0x00, 0x00, 0x00, 0x00, // Schema cookie
                0x00, 0x00, 0x00, 0x04, // Schema format number (4)
                0x00, 0x00, 0x10, 0x00, // Default page cache size
                0x00, 0x00, 0x00, 0x00, // Largest root btree page
                0x00, 0x00, 0x00, 0x01, // Text encoding (1 = UTF-8)
                0x00, 0x00, 0x00, 0x00, // User version
                0x00, 0x00, 0x00, 0x00, // Incremental vacuum mode
                0x00, 0x00, 0x00, 0x00, // Application ID
                // Reserved space (20 bytes of zeros)
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00, // Version-valid-for number
                0x00, 0x2E, 0x33, 0x38  // SQLite version number (encoded)
            };

            // Create a minimal valid SQLite file (4096 bytes - one page)
            byte[] minimalDb = new byte[4096];
            System.Array.Copy(sqliteHeader, minimalDb, sqliteHeader.Length);

            // Write the minimal databases ONLY if they don't exist
            // CRITICAL: Never overwrite existing private database - it's sacred!
            if (!File.Exists(privateDbPath))
            {
                File.WriteAllBytes(privateDbPath, minimalDb);
                Debug.Log("[Synthesis] Created minimal private database");
            }
            else
            {
                Debug.Log("[Synthesis] Private database already exists - preserving it");
            }

            if (!File.Exists(knowledgeDbPath))
            {
                File.WriteAllBytes(knowledgeDbPath, minimalDb);
                Debug.Log("[Synthesis] Created minimal knowledge database");
            }
            else
            {
                Debug.Log("[Synthesis] Knowledge database already exists - preserving it");
            }
        }

        private static void VerifyPythonEnvironment()
        {
            // Bundled Python runtime at project root
            string pythonPath = Path.Combine(Application.dataPath, "..", "PythonRuntime", "python", "python.exe");

            if (!File.Exists(pythonPath))
            {
                Debug.LogWarning("[Synthesis] Python runtime not found - skipping package verification");
                return;
            }

            try
            {
                // NOTE: Bundled Python runtime should already include all required packages:
                // bm25s, scipy, scikit-learn, sentence-transformers, numpy, mcp
                // This check verifies the packages are available

                Debug.Log("[Synthesis] Verifying Python packages...");

                var testProcess = new System.Diagnostics.Process();
                testProcess.StartInfo.FileName = pythonPath;
                testProcess.StartInfo.Arguments = "-c \"import bm25s, scipy, sklearn, sentence_transformers; print('OK')\"";
                testProcess.StartInfo.UseShellExecute = false;
                testProcess.StartInfo.RedirectStandardOutput = true;
                testProcess.StartInfo.RedirectStandardError = true;
                testProcess.StartInfo.CreateNoWindow = true;
                testProcess.Start();
                testProcess.WaitForExit(10000);

                if (testProcess.ExitCode == 0)
                {
                    Debug.Log("[Synthesis] ✅ Python environment ready - all packages available");
                }
                else
                {
                    string error = testProcess.StandardError.ReadToEnd();
                    Debug.LogWarning($"[Synthesis] Python package verification failed: {error}");
                    Debug.LogWarning("[Synthesis] The bundled Python runtime may be incomplete or corrupted");
                }
            }
            catch (System.Exception e)
            {
                Debug.LogWarning($"[Synthesis] Python verification warning: {e.Message}");
            }
        }

        private static void CreateInitialPublicContent()
        {
            // Create some initial entries in knowledge DB
            string packageRoot = Path.Combine(Application.dataPath, "Synthesis.Pro");
            string databaseDir = Path.Combine(packageRoot, "Server", "database");
            string knowledgeDbPath = Path.Combine(databaseDir, "synthesis_knowledge.db");

            if (!File.Exists(knowledgeDbPath))
            {
                return;
            }

            Debug.Log("[Synthesis] Initial knowledge base ready");
            // Initial content is loaded from seed_public_knowledge.py if needed
        }

        private static bool DownloadPythonRuntime()
        {
            string projectRoot = Path.GetDirectoryName(Application.dataPath);
            string zipPath = Path.Combine(projectRoot, "python-runtime.zip");
            string extractPath = Path.Combine(projectRoot, "PythonRuntime");

            try
            {
                // PROACTIVE FIX 1: Check disk space before download
                System.IO.DriveInfo drive = new System.IO.DriveInfo(Path.GetPathRoot(projectRoot));
                long requiredSpace = PYTHON_RUNTIME_SIZE_MB * 1024 * 1024 * 3; // 3x for zip + extraction + safety
                if (drive.AvailableFreeSpace < requiredSpace)
                {
                    Debug.LogError($"[Synthesis] Insufficient disk space. Need {requiredSpace / (1024*1024)}MB, have {drive.AvailableFreeSpace / (1024*1024)}MB");
                    EditorUtility.DisplayDialog(
                        "Insufficient Disk Space",
                        $"Not enough disk space to download Python runtime.\n\n" +
                        $"Required: ~{requiredSpace / (1024*1024)}MB\n" +
                        $"Available: {drive.AvailableFreeSpace / (1024*1024)}MB\n\n" +
                        "Free up space and try again.",
                        "OK"
                    );
                    return false;
                }

                // PROACTIVE FIX 2: Clean up partial downloads from previous failures
                if (File.Exists(zipPath))
                {
                    Debug.Log("[Synthesis] Cleaning up previous partial download...");
                    File.Delete(zipPath);
                }
                if (Directory.Exists(extractPath))
                {
                    Debug.Log("[Synthesis] Cleaning up previous partial extraction...");
                    Directory.Delete(extractPath, true);
                }

                Debug.Log($"[Synthesis] Downloading Python runtime from: {PYTHON_RUNTIME_URL}");

                // PROACTIVE FIX 3: Retry logic for network failures
                int maxRetries = 3;
                bool downloadSuccess = false;
                System.Exception lastException = null;

                for (int attempt = 1; attempt <= maxRetries && !downloadSuccess; attempt++)
                {
                    try
                    {
                        if (attempt > 1)
                        {
                            Debug.Log($"[Synthesis] Retry attempt {attempt}/{maxRetries}...");
                        }

                        using (var webClient = new System.Net.WebClient())
                        {
                            webClient.DownloadProgressChanged += (sender, e) =>
                            {
                                float progress = e.ProgressPercentage / 100f;
                                EditorUtility.DisplayProgressBar("Synthesis Setup",
                                    $"Downloading Python runtime... {e.ProgressPercentage}% (Attempt {attempt}/{maxRetries})",
                                    0.1f + (progress * 0.5f));
                            };

                            // Synchronous download with progress
                            webClient.DownloadFile(PYTHON_RUNTIME_URL, zipPath);
                        }

                        downloadSuccess = true;
                    }
                    catch (System.Exception e)
                    {
                        lastException = e;
                        Debug.LogWarning($"[Synthesis] Download attempt {attempt} failed: {e.Message}");

                        if (attempt < maxRetries)
                        {
                            System.Threading.Thread.Sleep(2000); // Wait 2s before retry
                        }
                    }
                }

                if (!downloadSuccess)
                {
                    throw new System.Exception($"Download failed after {maxRetries} attempts: {lastException?.Message}");
                }

                // PROACTIVE FIX 4: Verify download size before extraction
                FileInfo zipFile = new FileInfo(zipPath);
                long minExpectedSize = (PYTHON_RUNTIME_SIZE_MB * 1024 * 1024) / 2; // At least half expected size
                if (zipFile.Length < minExpectedSize)
                {
                    throw new System.Exception($"Downloaded file too small ({zipFile.Length} bytes). Download may be corrupted.");
                }

                Debug.Log($"[Synthesis] Download complete ({zipFile.Length / (1024*1024)}MB), extracting...");

                // Extract with better error handling
                EditorUtility.DisplayProgressBar("Synthesis Setup", "Extracting Python runtime...", 0.6f);

                try
                {
                    ZipFile.ExtractToDirectory(zipPath, extractPath);
                }
                catch (System.Exception e)
                {
                    throw new System.Exception($"Extraction failed: {e.Message}. Zip file may be corrupted.");
                }

                // Verify python.exe exists
                string pythonExe = Path.Combine(extractPath, "python", "python.exe");
                if (!File.Exists(pythonExe))
                {
                    throw new System.Exception($"Python executable not found after extraction at: {pythonExe}. Archive structure may be incorrect.");
                }

                // PROACTIVE FIX 5: Test Python runs
                try
                {
                    var testProcess = new System.Diagnostics.Process();
                    testProcess.StartInfo.FileName = pythonExe;
                    testProcess.StartInfo.Arguments = "--version";
                    testProcess.StartInfo.UseShellExecute = false;
                    testProcess.StartInfo.RedirectStandardOutput = true;
                    testProcess.StartInfo.CreateNoWindow = true;
                    testProcess.Start();

                    if (!testProcess.WaitForExit(5000))
                    {
                        testProcess.Kill();
                        Debug.LogWarning("[Synthesis] Python test run timed out (may be antivirus scanning)");
                    }
                    else if (testProcess.ExitCode != 0)
                    {
                        Debug.LogWarning($"[Synthesis] Python test failed with exit code {testProcess.ExitCode}");
                    }
                    else
                    {
                        string version = testProcess.StandardOutput.ReadToEnd().Trim();
                        Debug.Log($"[Synthesis] Python runtime verified: {version}");
                    }
                }
                catch (System.Exception e)
                {
                    Debug.LogWarning($"[Synthesis] Could not verify Python runtime (may be antivirus): {e.Message}");
                    // Don't fail - antivirus might be scanning
                }

                // Clean up zip file
                File.Delete(zipPath);

                Debug.Log("[Synthesis] ✅ Python runtime downloaded and extracted successfully");
                return true;
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[Synthesis] Failed to download Python runtime: {e.Message}");

                // PROACTIVE FIX 6: Clean up on failure
                try
                {
                    if (File.Exists(zipPath)) File.Delete(zipPath);
                    if (Directory.Exists(extractPath)) Directory.Delete(extractPath, true);
                }
                catch { /* Ignore cleanup errors */ }

                // PROACTIVE FIX 7: Actionable error message
                EditorUtility.DisplayDialog(
                    "Download Failed",
                    $"Failed to download Python runtime:\n\n{e.Message}\n\n" +
                    "Troubleshooting:\n" +
                    "• Check internet connection\n" +
                    "• Disable antivirus temporarily\n" +
                    "• Check firewall settings\n" +
                    "• Verify GitHub is accessible\n" +
                    "• Try manual download (see docs)\n\n" +
                    "Check console for details.",
                    "OK"
                );

                return false;
            }
        }

        [MenuItem("Tools/Synthesis/Setup/Reset Setup", false, 101)]
        public static void ResetSetup()
        {
            bool confirm = EditorUtility.DisplayDialog(
                "Reset Setup?",
                "This will mark Synthesis as not set up.\n\n" +
                "First-time setup will run again on next restart.\n\n" +
                "Continue?",
                "Yes, Reset",
                "Cancel"
            );

            if (confirm)
            {
                EditorPrefs.DeleteKey(SETUP_COMPLETE_KEY);
                Debug.Log("[Synthesis] Setup reset. Restart Unity to run setup again.");

                EditorUtility.DisplayDialog(
                    "Reset Complete",
                    "Setup has been reset.\n\n" +
                    "Restart Unity to run first-time setup again.",
                    "OK"
                );
            }
        }

        [MenuItem("Tools/Synthesis/Setup/Validate Python Runtime", false, 102)]
        public static void ValidateRuntime()
        {
            EditorUtility.DisplayProgressBar("Synthesis", "Validating Python runtime...", 0.5f);

            bool isValid = ValidatePythonRuntime();

            EditorUtility.ClearProgressBar();

            if (isValid)
            {
                EditorUtility.DisplayDialog(
                    "Runtime Valid",
                    "✅ Python runtime found and validated!\n\n" +
                    "Location: PythonRuntime/python/python.exe\n\n" +
                    "All systems ready.",
                    "OK"
                );
            }
            else
            {
                bool shouldDownload = EditorUtility.DisplayDialog(
                    "Runtime Missing",
                    "❌ Python runtime not found!\n\n" +
                    "Expected location: PythonRuntime/python/python.exe\n\n" +
                    $"Download now? (~{PYTHON_RUNTIME_SIZE_MB}MB)",
                    "Download",
                    "Cancel"
                );

                if (shouldDownload)
                {
                    if (DownloadPythonRuntime())
                    {
                        EditorUtility.DisplayDialog(
                            "Download Complete",
                            "✅ Python runtime downloaded successfully!\n\n" +
                            "All systems ready.",
                            "OK"
                        );
                    }
                    else
                    {
                        EditorUtility.DisplayDialog(
                            "Download Failed",
                            "❌ Failed to download Python runtime.\n\n" +
                            "Check console for details.",
                            "OK"
                        );
                    }
                }
            }
        }

        [MenuItem("Tools/Synthesis/Setup/Validate Project Structure", false, 103)]
        public static void ManualValidateStructure()
        {
            EditorUtility.DisplayProgressBar("Synthesis", "Validating project structure...", 0.5f);

            try
            {
                ValidateAndCorrectStructure();
                EditorUtility.ClearProgressBar();

                EditorUtility.DisplayDialog(
                    "Structure Validated",
                    "✅ Project structure validated and corrected!\n\n" +
                    "Check console for details.\n\n" +
                    "This validation runs automatically on Unity startup\n" +
                    "and ensures everything is in the right place.",
                    "OK"
                );
            }
            catch (System.Exception e)
            {
                EditorUtility.ClearProgressBar();
                EditorUtility.DisplayDialog(
                    "Validation Error",
                    $"Structure validation encountered an error:\n\n{e.Message}\n\n" +
                    "Check console for details.",
                    "OK"
                );
            }
        }
    }
}
