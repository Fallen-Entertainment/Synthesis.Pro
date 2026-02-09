using UnityEngine;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using Synthesis.Pro;

namespace Synthesis.Bridge
{
    /// <summary>
    /// Synthesis Manager - Integration Hub
    ///
    /// Coordinates communication between:
    /// - WebSocket Client (Python server connection)
    /// - SynLink (Unity command executor)
    /// - SynLinkExtended (Creative AI commands)
    ///
    /// Flow:
    ///   Python Server → WebSocket → Manager → SynLink → Execute
    ///   Execute Result → Manager → WebSocket → Python Server
    /// </summary>
    [DefaultExecutionOrder(-900)]
    [AddComponentMenu("Synthesis/Synthesis Manager")]
    public class SynthesisManager : MonoBehaviour
    {
        #region Singleton

        private static SynthesisManager instance;
        public static SynthesisManager Instance => instance;

        #endregion

        #region Settings

        [Header("Component References")]
        [SerializeField] private SynthesisWebSocketClient webSocketClient;
        [SerializeField] private SynLink synLink;
        [SerializeField] private SynLinkExtended synLinkExtended;

        [Header("Auto Setup")]
        [SerializeField] private bool autoCreateComponents = true;
        [SerializeField] private bool autoConnect = true;

        [Header("Server Management")]
        [SerializeField] private bool autoStartServer = true;
        [SerializeField] private string serverExecutableName = "websocket_server.py";
        [SerializeField] private float serverStartupDelay = 2f;

        #endregion

        #region State

        private bool isInitialized = false;
        private int commandsRouted = 0;
        private int resultsDelivered = 0;

        // Server process management
        private Process serverProcess = null;
        private bool serverStartedByUs = false;

        #endregion

        #region Unity Lifecycle

        private void Awake()
        {
            // Singleton
            if (instance != null && instance != this)
            {
                Destroy(gameObject);
                return;
            }

            instance = this;
            DontDestroyOnLoad(gameObject);

            // PROACTIVE FIX: Clean up orphaned Python processes from previous crashes
            CleanupOrphanedProcesses();

            // Ensure runtime directory exists - buttery and creamy setup
            SynthesisPaths.EnsureRuntimeExists();

            // Auto-create components if needed
            if (autoCreateComponents)
            {
                SetupComponents();
            }

            // Initialize integration
            InitializeIntegration();

            // Auto-start server if enabled
            if (autoStartServer)
            {
                StartServer();
            }

            Log("🎮 Synthesis Manager initialized!");
        }

        private void OnDestroy()
        {
            // Stop server if we started it
            StopServer();

            // Cleanup
            if (isInitialized)
            {
                CleanupIntegration();
            }

            if (instance == this)
            {
                instance = null;
            }
        }

        private void OnApplicationQuit()
        {
            // Ensure server is stopped on quit
            StopServer();
        }

        #endregion

        #region Component Setup

        private void SetupComponents()
        {
            // Find or create WebSocket client
            if (webSocketClient == null)
            {
                webSocketClient = FindObjectOfType<SynthesisWebSocketClient>();
                if (webSocketClient == null)
                {
                    var clientObj = new GameObject("SynthesisWebSocketClient");
                    clientObj.transform.SetParent(transform);
                    webSocketClient = clientObj.AddComponent<SynthesisWebSocketClient>();
                    Log("Created WebSocket client component");
                }
            }

            // Find or create SynLink
            if (synLink == null)
            {
                synLink = FindObjectOfType<SynLink>();
                if (synLink == null)
                {
                    var linkObj = new GameObject("SynLink");
                    linkObj.transform.SetParent(transform);
                    synLink = linkObj.AddComponent<SynLink>();
                    Log("Created SynLink component");
                }
            }

            // Find or create SynLinkExtended
            if (synLinkExtended == null)
            {
                synLinkExtended = FindObjectOfType<SynLinkExtended>();
                if (synLinkExtended == null)
                {
                    var extendedObj = new GameObject("SynLinkExtended");
                    extendedObj.transform.SetParent(transform);
                    synLinkExtended = extendedObj.AddComponent<SynLinkExtended>();
                    Log("Created SynLinkExtended component");
                }
            }
        }

        #endregion

        #region Integration

        private void InitializeIntegration()
        {
            if (isInitialized)
            {
                return;
            }

            // Connect WebSocket to command routing
            if (webSocketClient != null)
            {
                webSocketClient.OnConnected += HandleWebSocketConnected;
                webSocketClient.OnDisconnected += HandleWebSocketDisconnected;
                webSocketClient.OnCommandResult += HandleWebSocketMessage;
                webSocketClient.OnError += HandleWebSocketError;
                Log("✅ WebSocket events connected");
            }
            else
            {
                LogWarning("WebSocket client not found!");
            }

            // Connect SynLink result callback to WebSocket
            if (synLink != null)
            {
                synLink.OnResultReady = HandleSynLinkResult;
                Log("✅ SynLink results connected");
            }
            else
            {
                LogWarning("SynLink not found!");
            }

            // Connect SynLinkExtended result callback to WebSocket
            if (synLinkExtended != null)
            {
                synLinkExtended.OnResultReady = HandleSynLinkResult;
                Log("✅ SynLinkExtended results connected");
            }
            else
            {
                LogWarning("SynLinkExtended not found!");
            }

            isInitialized = true;
            Log("🔗 Integration complete!");
        }

        private void CleanupIntegration()
        {
            // Disconnect events
            if (webSocketClient != null)
            {
                webSocketClient.OnConnected -= HandleWebSocketConnected;
                webSocketClient.OnDisconnected -= HandleWebSocketDisconnected;
                webSocketClient.OnCommandResult -= HandleWebSocketMessage;
                webSocketClient.OnError -= HandleWebSocketError;
            }

            // Clear callbacks
            if (synLink != null)
            {
                synLink.OnResultReady = null;
            }

            if (synLinkExtended != null)
            {
                synLinkExtended.OnResultReady = null;
            }

            isInitialized = false;
        }

        #endregion

        #region WebSocket Event Handlers

        private void HandleWebSocketConnected()
        {
            Log("🌐 Connected to Synthesis.Pro server!");
        }

        private void HandleWebSocketDisconnected()
        {
            Log("🌐 Disconnected from server");
        }

        private void HandleWebSocketMessage(BridgeResult result)
        {
            // Check if this is a command from server (not a result)
            // For now, we only handle results from SynLink commands
            // Server-initiated commands would come through a different message type

            Log($"📨 Received message from server: {result.message}");
        }

        private void HandleWebSocketError(string error)
        {
            LogError($"WebSocket error: {error}");
        }

        #endregion

        #region Command Routing

        /// <summary>
        /// Route a command from WebSocket to SynLink
        /// </summary>
        public void RouteCommand(BridgeCommand command)
        {
            if (synLink == null)
            {
                LogError("Cannot route command: SynLink not available");
                return;
            }

            Log($"📥 Routing command: {command.type} (ID: {command.id})");

            // Queue command in SynLink (which validates and executes)
            synLink.QueueCommand(command);

            commandsRouted++;
        }

        #endregion

        #region Result Handling

        private void HandleSynLinkResult(BridgeResult result)
        {
            if (webSocketClient == null || !webSocketClient.IsConnected)
            {
                LogWarning($"Cannot send result: WebSocket not connected (ID: {result.commandId})");
                return;
            }

            Log($"📤 Sending result to server: {result.commandId} - {result.message}");

            // Send result back to Python server via WebSocket
            webSocketClient.SendResult(result);

            resultsDelivered++;
        }

        #endregion

        #region Public API

        /// <summary>
        /// Send a command to the Python server
        /// </summary>
        public void SendCommand(BridgeCommand command)
        {
            if (webSocketClient == null || !webSocketClient.IsConnected)
            {
                LogError("Cannot send command: Not connected to server");
                return;
            }

            webSocketClient.SendCommand(command);
        }

        /// <summary>
        /// Manually connect to server
        /// </summary>
        public void Connect()
        {
            if (webSocketClient != null)
            {
                webSocketClient.Connect();
            }
            else
            {
                LogError("WebSocket client not available");
            }
        }

        /// <summary>
        /// Manually disconnect from server
        /// </summary>
        public void Disconnect()
        {
            if (webSocketClient != null)
            {
                webSocketClient.Disconnect();
            }
        }

        /// <summary>
        /// Check if connected to server
        /// </summary>
        public bool IsConnected => webSocketClient != null && webSocketClient.IsConnected;

        /// <summary>
        /// Get integration statistics
        /// </summary>
        public IntegrationStats GetStats()
        {
            return new IntegrationStats
            {
                IsInitialized = isInitialized,
                IsConnected = IsConnected,
                CommandsRouted = commandsRouted,
                ResultsDelivered = resultsDelivered,
                WebSocketStats = webSocketClient?.GetStats(),
                SynLinkCommandsProcessed = synLink?.GetCommandsProcessed() ?? 0,
                ValidationStats = synLink?.GetValidationStats()
            };
        }

        /// <summary>
        /// Send a chat message to the AI
        /// </summary>
        public void SendChatMessage(string message, string context = "")
        {
            SendCommand(new BridgeCommand
            {
                id = $"chat_{System.DateTime.Now.Ticks}",
                type = "chat",
                parameters = new Dictionary<string, object>
                {
                    { "message", message },
                    { "context", context }
                }
            });
        }

        /// <summary>
        /// Search the knowledge base
        /// </summary>
        public void SearchKnowledge(string query, int topK = 10, bool privateDb = true)
        {
            SendCommand(new BridgeCommand
            {
                id = $"search_{System.DateTime.Now.Ticks}",
                type = "search_knowledge",
                parameters = new Dictionary<string, object>
                {
                    { "query", query },
                    { "top_k", topK },
                    { "private", privateDb }
                }
            });
        }

        #endregion

        #region Server Management

        /// <summary>
        /// Start the Python WebSocket server process
        /// </summary>
        private async void StartServer()
        {
            if (serverProcess != null)
            {
                Log("Server process already running");
                return;
            }

            try
            {
                // Find server script path
                string serverPath = FindServerPath();
                if (string.IsNullOrEmpty(serverPath))
                {
                    LogError("Could not find server script. Please ensure " + serverExecutableName + " exists in Synthesis.Pro/Server/");
                    return;
                }

                Log($"Starting server: {serverPath}");

                // Use bundled Python runtime (buttery and creamy!)
                string pythonExe = Path.Combine(Application.dataPath, "..", "PythonRuntime", "python", "python.exe");
                if (!File.Exists(pythonExe))
                {
                    LogError($"Bundled Python runtime not found at: {pythonExe}");
                    return;
                }

                // Create process start info
                ProcessStartInfo startInfo = new ProcessStartInfo
                {
                    FileName = pythonExe,
                    Arguments = $"\"{serverPath}\"",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true,
                    WorkingDirectory = Path.GetDirectoryName(serverPath)
                };

                // Start process
                serverProcess = new Process { StartInfo = startInfo };

                // Log server output
                serverProcess.OutputDataReceived += (sender, args) =>
                {
                    if (!string.IsNullOrEmpty(args.Data))
                    {
                        Log($"[Server] {args.Data}");
                    }
                };

                serverProcess.ErrorDataReceived += (sender, args) =>
                {
                    if (!string.IsNullOrEmpty(args.Data))
                    {
                        LogWarning($"[Server] {args.Data}");
                    }
                };

                serverProcess.Start();
                serverProcess.BeginOutputReadLine();
                serverProcess.BeginErrorReadLine();

                serverStartedByUs = true;
                Log("✅ Server process started");

                // Wait for server to initialize
                await System.Threading.Tasks.Task.Delay((int)(serverStartupDelay * 1000));

                // Auto-connect if enabled
                if (autoConnect && webSocketClient != null && !webSocketClient.IsConnected)
                {
                    Log("Auto-connecting to server...");
                    webSocketClient.Connect();
                }
            }
            catch (System.Exception ex)
            {
                LogError($"Failed to start server: {ex.Message}");
                LogWarning("Please ensure Python is installed and in PATH");
                serverProcess = null;
            }
        }

        /// <summary>
        /// Stop the Python WebSocket server process
        /// ENHANCED: Better error handling and forced cleanup
        /// </summary>
        private void StopServer()
        {
            if (serverProcess == null || !serverStartedByUs)
            {
                return;
            }

            try
            {
                if (!serverProcess.HasExited)
                {
                    Log("Stopping server process...");

                    try
                    {
                        // Try graceful shutdown first
                        serverProcess.Kill();
                        if (!serverProcess.WaitForExit(3000))
                        {
                            // Force kill if still running
                            serverProcess.Kill();
                            serverProcess.WaitForExit(1000);
                        }
                    }
                    catch (System.Exception ex)
                    {
                        LogWarning($"Process termination warning: {ex.Message}");
                    }

                    Log("Server process stopped");
                }

                serverProcess.Dispose();
            }
            catch (System.Exception ex)
            {
                LogWarning($"Error stopping server: {ex.Message}");
            }
            finally
            {
                serverProcess = null;
                serverStartedByUs = false;
            }
        }

        /// <summary>
        /// Clean up orphaned Python processes from previous Unity crashes
        /// PROACTIVE: Prevents port conflicts and resource leaks
        /// Simplified approach using process path checking
        /// </summary>
        private void CleanupOrphanedProcesses()
        {
            try
            {
                // Find all python.exe processes
                var pythonProcesses = Process.GetProcessesByName("python");

                if (pythonProcesses.Length > 0)
                {
                    Log($"Checking {pythonProcesses.Length} Python process(es) for orphans...");

                    foreach (var process in pythonProcesses)
                    {
                        try
                        {
                            // Check if process is from our PythonRuntime
                            if (process.MainModule != null)
                            {
                                string exePath = process.MainModule.FileName.ToLower();

                                // Only kill if it's from our PythonRuntime or Synthesis.Pro folder
                                if (exePath.Contains("pythonruntime") ||
                                    exePath.Contains("synthesis.pro") ||
                                    exePath.Contains("synthesis-pro"))
                                {
                                    Log($"Cleaning up orphaned Python process (PID: {process.Id})");
                                    process.Kill();
                                    process.WaitForExit(2000);
                                }
                            }
                        }
                        catch
                        {
                            // Process may have exited, access denied, or system process - safely ignore
                        }
                        finally
                        {
                            process.Dispose();
                        }
                    }
                }
            }
            catch (System.Exception ex)
            {
                // Don't fail startup if cleanup fails
                LogWarning($"Orphaned process cleanup warning: {ex.Message}");
            }
        }

        /// <summary>
        /// Find the server script path
        /// </summary>
        private string FindServerPath()
        {
            // Try centralized path first (buttery!)
            string primaryPath = Path.Combine(SynthesisPaths.Server, serverExecutableName);
            if (File.Exists(primaryPath))
            {
                return primaryPath;
            }

            // Fallback paths for package installations
            string[] searchPaths = new string[]
            {
                Path.Combine(Application.dataPath, "..", "Packages", "Synthesis.Pro", "Server", serverExecutableName),
                Path.Combine(Application.dataPath, "..", "Packages", "com.synthesis.pro", "Server", serverExecutableName),
                Path.Combine(Application.dataPath, "..", "Synthesis.Pro", "Server", serverExecutableName)
            };

            foreach (string path in searchPaths)
            {
                string fullPath = Path.GetFullPath(path);
                if (File.Exists(fullPath))
                {
                    return fullPath;
                }
            }

            return null;
        }

        /// <summary>
        /// Check if server is running
        /// </summary>
        public bool IsServerRunning()
        {
            return serverProcess != null && !serverProcess.HasExited;
        }

        #endregion

        #region Logging

        private void Log(string message)
        {
            UnityEngine.Debug.Log($"[SynthesisManager] {message}");
        }

        private void LogWarning(string message)
        {
            UnityEngine.Debug.LogWarning($"[SynthesisManager] {message}");
        }

        private void LogError(string message)
        {
            UnityEngine.Debug.LogError($"[SynthesisManager] {message}");
        }

        #endregion
    }

    #region Data Structures

    [System.Serializable]
    public class IntegrationStats
    {
        public bool IsInitialized;
        public bool IsConnected;
        public int CommandsRouted;
        public int ResultsDelivered;
        public ConnectionStats WebSocketStats;
        public int SynLinkCommandsProcessed;
        public ValidationStats ValidationStats;

        public override string ToString()
        {
            return $"Integration Stats:\n" +
                   $"  Initialized: {IsInitialized}\n" +
                   $"  Connected: {IsConnected}\n" +
                   $"  Commands Routed: {CommandsRouted}\n" +
                   $"  Results Delivered: {ResultsDelivered}\n" +
                   $"  SynLink Processed: {SynLinkCommandsProcessed}";
        }
    }

    #endregion
}
