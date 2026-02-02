using UnityEngine;
using System;
using System.Collections.Generic;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace Synthesis.Bridge
{
    /// <summary>
    /// WebSocket client for Synthesis.Pro
    ///
    /// Connects Unity to the Python WebSocket server for real-time
    /// AI-powered development assistance.
    ///
    /// Features:
    /// - Automatic reconnection
    /// - Command queueing
    /// - Connection health monitoring
    /// - Event-based result handling
    /// </summary>
    [AddComponentMenu("Synthesis/WebSocket Client")]
    public class SynthesisWebSocketClient : MonoBehaviour
    {
        #region Singleton

        private static SynthesisWebSocketClient instance;
        public static SynthesisWebSocketClient Instance => instance;

        #endregion

        #region Settings

        [Header("Connection Settings")]
        [SerializeField] private string serverHost = "localhost";
        [SerializeField] private int serverPort = 8765;
        [SerializeField] private bool autoConnect = true;
        [SerializeField] private bool autoReconnect = true;
        [SerializeField] private float reconnectDelay = 5f;

        [Header("Health Check")]
        [SerializeField] private float pingInterval = 30f;
        [SerializeField] private float connectionTimeout = 10f;

        #endregion

        #region State

        private ClientWebSocket webSocket;
        private CancellationTokenSource cancellationToken;

        private bool isConnected = false;
        private bool isConnecting = false;
        private float lastPingTime = 0f;
        private float reconnectTimer = 0f;

        // Message queue for thread safety
        private Queue<string> incomingMessages = new Queue<string>();
        private Queue<string> outgoingMessages = new Queue<string>();
        private object messageLock = new object();

        // Statistics
        private int messagesSent = 0;
        private int messagesReceived = 0;
        private DateTime connectionTime;

        #endregion

        #region Events

        public event Action OnConnected;
        public event Action OnDisconnected;
        public event Action<BridgeResult> OnCommandResult;
        public event Action<string> OnError;

        #endregion

        #region Unity Lifecycle

        private void Awake()
        {
            if (instance != null && instance != this)
            {
                Destroy(gameObject);
                return;
            }

            instance = this;
            DontDestroyOnLoad(gameObject);

            Log("WebSocket Client initialized");
        }

        private void Start()
        {
            if (autoConnect)
            {
                Connect();
            }
        }

        private void Update()
        {
            // Process incoming messages on main thread
            ProcessIncomingMessages();

            // Send queued outgoing messages
            ProcessOutgoingMessages();

            // Handle reconnection
            if (!isConnected && autoReconnect && !isConnecting)
            {
                reconnectTimer += Time.deltaTime;
                if (reconnectTimer >= reconnectDelay)
                {
                    reconnectTimer = 0f;
                    Connect();
                }
            }

            // Send periodic pings
            if (isConnected && Time.time - lastPingTime >= pingInterval)
            {
                lastPingTime = Time.time;
                SendPing();
            }
        }

        private void OnDestroy()
        {
            Disconnect();

            if (instance == this)
            {
                instance = null;
            }
        }

        private void OnApplicationQuit()
        {
            Disconnect();
        }

        #endregion

        #region Connection Management

        /// <summary>
        /// Connect to WebSocket server
        /// </summary>
        public async void Connect()
        {
            if (isConnected || isConnecting)
            {
                Log("Already connected or connecting");
                return;
            }

            isConnecting = true;
            Log($"Connecting to ws://{serverHost}:{serverPort}...");

            try
            {
                // Create WebSocket
                webSocket = new ClientWebSocket();
                cancellationToken = new CancellationTokenSource();

                // Connect
                Uri serverUri = new Uri($"ws://{serverHost}:{serverPort}");
                await webSocket.ConnectAsync(serverUri, cancellationToken.Token);

                isConnected = true;
                isConnecting = false;
                connectionTime = DateTime.Now;
                reconnectTimer = 0f;

                Log("✅ Connected to Synthesis.Pro server!");

                // Start receiving messages
                _ = ReceiveLoop();

                // Notify listeners
                OnConnected?.Invoke();
            }
            catch (Exception ex)
            {
                isConnecting = false;
                isConnected = false;
                LogError($"Connection failed: {ex.Message}");
                OnError?.Invoke($"Connection failed: {ex.Message}");
            }
        }

        /// <summary>
        /// Disconnect from server
        /// </summary>
        public async void Disconnect()
        {
            if (!isConnected || webSocket == null)
            {
                return;
            }

            Log("Disconnecting from server...");

            try
            {
                cancellationToken?.Cancel();

                if (webSocket.State == WebSocketState.Open)
                {
                    await webSocket.CloseAsync(WebSocketCloseStatus.NormalClosure, "Client disconnect", CancellationToken.None);
                }

                webSocket?.Dispose();
                webSocket = null;

                isConnected = false;
                Log("Disconnected from server");

                OnDisconnected?.Invoke();
            }
            catch (Exception ex)
            {
                LogError($"Disconnect error: {ex.Message}");
            }
        }

        /// <summary>
        /// Check if connected to server
        /// </summary>
        public bool IsConnected => isConnected;

        #endregion

        #region Message Handling

        private async Task ReceiveLoop()
        {
            var buffer = new byte[1024 * 4];

            try
            {
                while (webSocket.State == WebSocketState.Open && !cancellationToken.Token.IsCancellationRequested)
                {
                    var result = await webSocket.ReceiveAsync(new ArraySegment<byte>(buffer), cancellationToken.Token);

                    if (result.MessageType == WebSocketMessageType.Close)
                    {
                        Log("Server closed connection");
                        break;
                    }

                    if (result.MessageType == WebSocketMessageType.Text)
                    {
                        string message = Encoding.UTF8.GetString(buffer, 0, result.Count);

                        // Queue message for main thread processing
                        lock (messageLock)
                        {
                            incomingMessages.Enqueue(message);
                            messagesReceived++;
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                if (!cancellationToken.Token.IsCancellationRequested)
                {
                    LogError($"Receive error: {ex.Message}");
                }
            }
            finally
            {
                isConnected = false;
                OnDisconnected?.Invoke();
            }
        }

        private void ProcessIncomingMessages()
        {
            lock (messageLock)
            {
                while (incomingMessages.Count > 0)
                {
                    string message = incomingMessages.Dequeue();
                    HandleIncomingMessage(message);
                }
            }
        }

        private void HandleIncomingMessage(string message)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(message);

                string messageType = data.GetValueOrDefault("type")?.ToString() ?? "result";

                if (messageType == "connection")
                {
                    // Connection acknowledgment
                    Log($"Server: {data.GetValueOrDefault("message")}");
                }
                else
                {
                    // Command result
                    var result = JsonConvert.DeserializeObject<BridgeResult>(message);
                    OnCommandResult?.Invoke(result);
                }
            }
            catch (Exception ex)
            {
                LogError($"Failed to parse message: {ex.Message}");
            }
        }

        private void ProcessOutgoingMessages()
        {
            lock (messageLock)
            {
                while (outgoingMessages.Count > 0)
                {
                    string message = outgoingMessages.Dequeue();
                    _ = SendMessageAsync(message);
                }
            }
        }

        private async Task SendMessageAsync(string message)
        {
            if (!isConnected || webSocket == null || webSocket.State != WebSocketState.Open)
            {
                LogError("Cannot send message: Not connected");
                return;
            }

            try
            {
                byte[] buffer = Encoding.UTF8.GetBytes(message);
                await webSocket.SendAsync(new ArraySegment<byte>(buffer), WebSocketMessageType.Text, true, cancellationToken.Token);
                messagesSent++;
            }
            catch (Exception ex)
            {
                LogError($"Send error: {ex.Message}");
                isConnected = false;
            }
        }

        #endregion

        #region Public API

        /// <summary>
        /// Send a command to the server
        /// </summary>
        public void SendCommand(BridgeCommand command)
        {
            if (!isConnected)
            {
                LogError("Cannot send command: Not connected");
                return;
            }

            try
            {
                string json = JsonConvert.SerializeObject(command);

                lock (messageLock)
                {
                    outgoingMessages.Enqueue(json);
                }
            }
            catch (Exception ex)
            {
                LogError($"Failed to serialize command: {ex.Message}");
            }
        }

        /// <summary>
        /// Send a ping to check connection health
        /// </summary>
        public void SendPing()
        {
            SendCommand(new BridgeCommand
            {
                id = $"ping_{DateTime.Now.Ticks}",
                type = "ping",
                parameters = new Dictionary<string, object>()
            });
        }

        /// <summary>
        /// Get connection statistics
        /// </summary>
        public ConnectionStats GetStats()
        {
            return new ConnectionStats
            {
                IsConnected = isConnected,
                MessagesSent = messagesSent,
                MessagesReceived = messagesReceived,
                UptimeSeconds = isConnected ? (DateTime.Now - connectionTime).TotalSeconds : 0,
                ServerHost = serverHost,
                ServerPort = serverPort
            };
        }

        #endregion

        #region Logging

        private void Log(string message)
        {
            Debug.Log($"[WebSocketClient] {message}");
        }

        private void LogError(string message)
        {
            Debug.LogError($"[WebSocketClient] {message}");
        }

        #endregion
    }

    #region Data Structures

    [Serializable]
    public class ConnectionStats
    {
        public bool IsConnected;
        public int MessagesSent;
        public int MessagesReceived;
        public double UptimeSeconds;
        public string ServerHost;
        public int ServerPort;
    }

    #endregion
}
