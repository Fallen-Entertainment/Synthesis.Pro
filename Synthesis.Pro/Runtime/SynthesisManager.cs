using UnityEngine;
using System.Collections.Generic;

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

        #endregion

        #region State

        private bool isInitialized = false;
        private int commandsRouted = 0;
        private int resultsDelivered = 0;

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

            // Auto-create components if needed
            if (autoCreateComponents)
            {
                SetupComponents();
            }

            // Initialize integration
            InitializeIntegration();

            Log("🎮 Synthesis Manager initialized!");
        }

        private void OnDestroy()
        {
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

            // Auto-connect if enabled
            if (autoConnect && webSocketClient != null && !webSocketClient.IsConnected)
            {
                Log("Auto-connecting to server...");
                webSocketClient.Connect();
            }
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

        #region Logging

        private void Log(string message)
        {
            Debug.Log($"[SynthesisManager] {message}");
        }

        private void LogWarning(string message)
        {
            Debug.LogWarning($"[SynthesisManager] {message}");
        }

        private void LogError(string message)
        {
            Debug.LogError($"[SynthesisManager] {message}");
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
