using UnityEngine;
using UnityEditor;
using System.Collections.Generic;
using Synthesis.Bridge;

namespace Synthesis.Editor
{
    /// <summary>
    /// Synthesis.Pro Editor Window
    ///
    /// Provides a clean interface for developers to:
    /// - Monitor WebSocket connection status
    /// - Send chat messages to AI
    /// - Search knowledge base
    /// - View system statistics
    /// - Control connection state
    /// </summary>
    public class SynthesisProWindow : EditorWindow
    {
        #region Window Setup

        [MenuItem("Window/Synthesis.Pro")]
        public static void ShowWindow()
        {
            var window = GetWindow<SynthesisProWindow>("Synthesis.Pro");
            window.minSize = new Vector2(400, 500);
            window.Show();
        }

        #endregion

        #region State

        private Vector2 scrollPosition;
        private int selectedTab = 0;
        private readonly string[] tabNames = { "Monitor", "Chat", "Search", "Database", "Stats" };

        // Chat state
        private string chatMessage = "";
        private string chatContext = "";
        private Vector2 chatScrollPosition;
        private List<ChatMessage> chatHistory = new List<ChatMessage>();

        // Search state
        private string searchQuery = "";
        private int searchTopK = 10;
        private bool searchPrivate = true;
        private Vector2 searchScrollPosition;
        private List<SearchResult> searchResults = new List<SearchResult>();

        // Database state
        private Vector2 databaseScrollPosition;
        private List<BackupInfo> backupsList = new List<BackupInfo>();
        private string selectedBackup = "";
        private bool showClearConfirmation = false;

        // UI Style cache
        private GUIStyle headerStyle;
        private GUIStyle statusConnectedStyle;
        private GUIStyle statusDisconnectedStyle;
        private GUIStyle messageBoxStyle;

        #endregion

        #region Unity Lifecycle

        private void OnEnable()
        {
            EditorApplication.update += Repaint;
        }

        private void OnDisable()
        {
            EditorApplication.update -= Repaint;
        }

        private void OnGUI()
        {
            InitializeStyles();

            DrawHeader();
            DrawConnectionStatus();

            EditorGUILayout.Space(10);

            // Tab selection
            selectedTab = GUILayout.Toolbar(selectedTab, tabNames);

            EditorGUILayout.Space(5);

            // Draw selected tab content
            scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition);
            {
                switch (selectedTab)
                {
                    case 0: DrawMonitorTab(); break;
                    case 1: DrawChatTab(); break;
                    case 2: DrawSearchTab(); break;
                    case 3: DrawDatabaseTab(); break;
                    case 4: DrawStatsTab(); break;
                }
            }
            EditorGUILayout.EndScrollView();
        }

        #endregion

        #region UI Styles

        private void InitializeStyles()
        {
            if (headerStyle == null)
            {
                headerStyle = new GUIStyle(EditorStyles.boldLabel)
                {
                    fontSize = 16,
                    alignment = TextAnchor.MiddleCenter,
                    padding = new RectOffset(0, 0, 10, 10)
                };
            }

            if (statusConnectedStyle == null)
            {
                statusConnectedStyle = new GUIStyle(EditorStyles.label)
                {
                    normal = { textColor = new Color(0.2f, 0.8f, 0.2f) },
                    fontStyle = FontStyle.Bold,
                    alignment = TextAnchor.MiddleCenter
                };
            }

            if (statusDisconnectedStyle == null)
            {
                statusDisconnectedStyle = new GUIStyle(EditorStyles.label)
                {
                    normal = { textColor = new Color(0.8f, 0.2f, 0.2f) },
                    fontStyle = FontStyle.Bold,
                    alignment = TextAnchor.MiddleCenter
                };
            }

            if (messageBoxStyle == null)
            {
                messageBoxStyle = new GUIStyle(EditorStyles.helpBox)
                {
                    padding = new RectOffset(10, 10, 10, 10),
                    wordWrap = true
                };
            }
        }

        #endregion

        #region Header & Status

        private void DrawHeader()
        {
            EditorGUILayout.LabelField("Synthesis.Pro", headerStyle);
            EditorGUILayout.LabelField("AI-Powered Unity Development", EditorStyles.centeredGreyMiniLabel);
        }

        private void DrawConnectionStatus()
        {
            var manager = SynthesisManager.Instance;
            bool isConnected = manager != null && manager.IsConnected;

            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            {
                string statusText = isConnected ? "● CONNECTED" : "○ DISCONNECTED";
                var statusStyle = isConnected ? statusConnectedStyle : statusDisconnectedStyle;
                EditorGUILayout.LabelField(statusText, statusStyle);

                EditorGUILayout.BeginHorizontal();
                {
                    GUILayout.FlexibleSpace();

                    GUI.enabled = !isConnected;
                    if (GUILayout.Button("Connect", GUILayout.Width(100)))
                    {
                        ConnectToServer();
                    }
                    GUI.enabled = true;

                    GUI.enabled = isConnected;
                    if (GUILayout.Button("Disconnect", GUILayout.Width(100)))
                    {
                        DisconnectFromServer();
                    }
                    GUI.enabled = true;

                    GUILayout.FlexibleSpace();
                }
                EditorGUILayout.EndHorizontal();
            }
            EditorGUILayout.EndVertical();
        }

        #endregion

        #region Monitor Tab

        private void DrawMonitorTab()
        {
            var manager = SynthesisManager.Instance;

            if (manager == null)
            {
                EditorGUILayout.HelpBox("SynthesisManager not found in scene. Add it from: GameObject > Synthesis > Create Manager", MessageType.Warning);

                if (GUILayout.Button("Create SynthesisManager"))
                {
                    CreateSynthesisManager();
                }
                return;
            }

            EditorGUILayout.LabelField("System Monitor", EditorStyles.boldLabel);
            EditorGUILayout.Space(5);

            var stats = manager.GetStats();

            // Connection Info
            DrawStatSection("Connection", new Dictionary<string, string>
            {
                { "Status", stats.IsConnected ? "Connected" : "Disconnected" },
                { "Initialized", stats.IsInitialized ? "Yes" : "No" }
            });

            // Integration Stats
            DrawStatSection("Integration", new Dictionary<string, string>
            {
                { "Commands Routed", stats.CommandsRouted.ToString() },
                { "Results Delivered", stats.ResultsDelivered.ToString() },
                { "SynLink Processed", stats.SynLinkCommandsProcessed.ToString() }
            });

            // WebSocket Stats
            if (stats.WebSocketStats != null)
            {
                DrawStatSection("WebSocket", new Dictionary<string, string>
                {
                    { "Messages Sent", stats.WebSocketStats.MessagesSent.ToString() },
                    { "Messages Received", stats.WebSocketStats.MessagesReceived.ToString() },
                    { "Uptime", FormatUptime(stats.WebSocketStats.UptimeSeconds) },
                    { "Server", $"{stats.WebSocketStats.ServerHost}:{stats.WebSocketStats.ServerPort}" }
                });
            }

            // Validation Stats
            if (stats.ValidationStats != null)
            {
                DrawStatSection("Validation", new Dictionary<string, string>
                {
                    { "Total Validated", stats.ValidationStats.TotalValidated.ToString() },
                    { "Passed", stats.ValidationStats.Passed.ToString() },
                    { "Failed", stats.ValidationStats.Failed.ToString() },
                    { "Success Rate", $"{stats.ValidationStats.SuccessRate:P1}" }
                });
            }

            EditorGUILayout.Space(10);

            // Quick Actions
            EditorGUILayout.LabelField("Quick Actions", EditorStyles.boldLabel);
            EditorGUILayout.Space(5);

            GUI.enabled = stats.IsConnected;
            if (GUILayout.Button("Send Ping"))
            {
                SendPing();
            }
            GUI.enabled = true;
        }

        private void DrawStatSection(string title, Dictionary<string, string> stats)
        {
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            {
                EditorGUILayout.LabelField(title, EditorStyles.boldLabel);
                EditorGUI.indentLevel++;

                foreach (var stat in stats)
                {
                    EditorGUILayout.BeginHorizontal();
                    EditorGUILayout.LabelField(stat.Key, GUILayout.Width(150));
                    EditorGUILayout.LabelField(stat.Value, EditorStyles.wordWrappedLabel);
                    EditorGUILayout.EndHorizontal();
                }

                EditorGUI.indentLevel--;
            }
            EditorGUILayout.EndVertical();

            EditorGUILayout.Space(5);
        }

        #endregion

        #region Chat Tab

        private void DrawChatTab()
        {
            var manager = SynthesisManager.Instance;

            if (manager == null || !manager.IsConnected)
            {
                EditorGUILayout.HelpBox("Connect to server to use chat features.", MessageType.Info);
                return;
            }

            EditorGUILayout.LabelField("AI Chat", EditorStyles.boldLabel);
            EditorGUILayout.Space(5);

            // Chat history
            EditorGUILayout.LabelField("Conversation", EditorStyles.boldLabel);
            chatScrollPosition = EditorGUILayout.BeginScrollView(chatScrollPosition, GUILayout.Height(200));
            {
                if (chatHistory.Count == 0)
                {
                    EditorGUILayout.LabelField("No messages yet. Start a conversation!", EditorStyles.centeredGreyMiniLabel);
                }
                else
                {
                    foreach (var msg in chatHistory)
                    {
                        DrawChatMessage(msg);
                    }
                }
            }
            EditorGUILayout.EndScrollView();

            EditorGUILayout.Space(10);

            // Message input
            EditorGUILayout.LabelField("New Message", EditorStyles.boldLabel);

            EditorGUILayout.LabelField("Message:", EditorStyles.miniLabel);
            chatMessage = EditorGUILayout.TextArea(chatMessage, GUILayout.Height(60));

            EditorGUILayout.Space(5);

            EditorGUILayout.LabelField("Context (optional):", EditorStyles.miniLabel);
            chatContext = EditorGUILayout.TextField(chatContext);

            EditorGUILayout.Space(5);

            GUI.enabled = !string.IsNullOrWhiteSpace(chatMessage);
            if (GUILayout.Button("Send Message"))
            {
                SendChatMessage();
            }
            GUI.enabled = true;
        }

        private void DrawChatMessage(ChatMessage msg)
        {
            var bgColor = msg.IsUser ? new Color(0.3f, 0.3f, 0.4f, 0.5f) : new Color(0.2f, 0.4f, 0.3f, 0.5f);

            EditorGUILayout.BeginVertical(messageBoxStyle);
            {
                var originalBgColor = GUI.backgroundColor;
                GUI.backgroundColor = bgColor;

                EditorGUILayout.LabelField(msg.IsUser ? "You:" : "AI:", EditorStyles.boldLabel);
                EditorGUILayout.LabelField(msg.Message, EditorStyles.wordWrappedLabel);
                EditorGUILayout.LabelField(msg.Timestamp, EditorStyles.miniLabel);

                GUI.backgroundColor = originalBgColor;
            }
            EditorGUILayout.EndVertical();

            EditorGUILayout.Space(3);
        }

        #endregion

        #region Search Tab

        private void DrawSearchTab()
        {
            var manager = SynthesisManager.Instance;

            if (manager == null || !manager.IsConnected)
            {
                EditorGUILayout.HelpBox("Connect to server to use search features.", MessageType.Info);
                return;
            }

            EditorGUILayout.LabelField("Knowledge Search", EditorStyles.boldLabel);
            EditorGUILayout.Space(5);

            // Search input
            EditorGUILayout.LabelField("Search Query:", EditorStyles.miniLabel);
            searchQuery = EditorGUILayout.TextField(searchQuery);

            EditorGUILayout.Space(5);

            EditorGUILayout.BeginHorizontal();
            {
                EditorGUILayout.LabelField("Top K Results:", GUILayout.Width(100));
                searchTopK = EditorGUILayout.IntSlider(searchTopK, 1, 50);
            }
            EditorGUILayout.EndHorizontal();

            searchPrivate = EditorGUILayout.Toggle("Search Private Database", searchPrivate);

            EditorGUILayout.Space(5);

            GUI.enabled = !string.IsNullOrWhiteSpace(searchQuery);
            if (GUILayout.Button("Search"))
            {
                SearchKnowledge();
            }
            GUI.enabled = true;

            EditorGUILayout.Space(10);

            // Search results
            if (searchResults.Count > 0)
            {
                EditorGUILayout.LabelField($"Results ({searchResults.Count}):", EditorStyles.boldLabel);
                searchScrollPosition = EditorGUILayout.BeginScrollView(searchScrollPosition);
                {
                    foreach (var result in searchResults)
                    {
                        DrawSearchResult(result);
                    }
                }
                EditorGUILayout.EndScrollView();
            }
        }

        private void DrawSearchResult(SearchResult result)
        {
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            {
                EditorGUILayout.LabelField(result.Title, EditorStyles.boldLabel);
                EditorGUILayout.LabelField(result.Content, EditorStyles.wordWrappedLabel);
                EditorGUILayout.LabelField($"Relevance: {result.Score:F3}", EditorStyles.miniLabel);
            }
            EditorGUILayout.EndVertical();

            EditorGUILayout.Space(3);
        }

        #endregion

        #region Database Tab

        private void DrawDatabaseTab()
        {
            var manager = SynthesisManager.Instance;

            if (manager == null || !manager.IsConnected)
            {
                EditorGUILayout.HelpBox("Connect to server to use database management features.", MessageType.Info);
                return;
            }

            EditorGUILayout.LabelField("Private Database Management", EditorStyles.boldLabel);
            EditorGUILayout.Space(5);

            EditorGUILayout.HelpBox(
                "Your private database contains your relationship history with your AI partner. " +
                "This is personal data that should be backed up regularly.",
                MessageType.Info
            );

            EditorGUILayout.Space(10);

            // Backup Section
            EditorGUILayout.LabelField("Backup", EditorStyles.boldLabel);
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            {
                EditorGUILayout.LabelField("Create a timestamped backup of your private database.", EditorStyles.wordWrappedLabel);
                EditorGUILayout.Space(5);

                if (GUILayout.Button("Backup Private Database"))
                {
                    BackupPrivateDatabase();
                }
            }
            EditorGUILayout.EndVertical();

            EditorGUILayout.Space(10);

            // Restore Section
            EditorGUILayout.LabelField("Restore", EditorStyles.boldLabel);
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            {
                EditorGUILayout.LabelField("Restore from a previous backup.", EditorStyles.wordWrappedLabel);
                EditorGUILayout.Space(5);

                EditorGUILayout.BeginHorizontal();
                {
                    if (GUILayout.Button("Refresh Backups List", GUILayout.Width(150)))
                    {
                        RefreshBackupsList();
                    }

                    EditorGUILayout.LabelField($"({backupsList.Count} backups)", EditorStyles.miniLabel);
                }
                EditorGUILayout.EndHorizontal();

                EditorGUILayout.Space(5);

                if (backupsList.Count > 0)
                {
                    databaseScrollPosition = EditorGUILayout.BeginScrollView(databaseScrollPosition, GUILayout.Height(150));
                    {
                        foreach (var backup in backupsList)
                        {
                            EditorGUILayout.BeginHorizontal(EditorStyles.helpBox);
                            {
                                bool isSelected = selectedBackup == backup.Filename;
                                bool wasSelected = isSelected;
                                isSelected = EditorGUILayout.Toggle(isSelected, GUILayout.Width(20));

                                if (isSelected && !wasSelected)
                                {
                                    selectedBackup = backup.Filename;
                                }
                                else if (!isSelected && wasSelected)
                                {
                                    selectedBackup = "";
                                }

                                EditorGUILayout.BeginVertical();
                                {
                                    EditorGUILayout.LabelField(backup.Filename, EditorStyles.boldLabel);
                                    EditorGUILayout.LabelField($"Size: {FormatBytes(backup.Size)} | Modified: {backup.Modified}", EditorStyles.miniLabel);
                                }
                                EditorGUILayout.EndVertical();
                            }
                            EditorGUILayout.EndHorizontal();
                            EditorGUILayout.Space(2);
                        }
                    }
                    EditorGUILayout.EndScrollView();

                    EditorGUILayout.Space(5);

                    GUI.enabled = !string.IsNullOrEmpty(selectedBackup);
                    if (GUILayout.Button("Restore Selected Backup"))
                    {
                        if (EditorUtility.DisplayDialog(
                            "Restore Backup",
                            $"Are you sure you want to restore from '{selectedBackup}'?\n\n" +
                            "Your current database will be backed up before restore.",
                            "Restore",
                            "Cancel"))
                        {
                            RestorePrivateDatabase(selectedBackup);
                        }
                    }
                    GUI.enabled = true;
                }
                else
                {
                    EditorGUILayout.LabelField("No backups found. Click 'Refresh Backups List' to check.", EditorStyles.centeredGreyMiniLabel);
                }
            }
            EditorGUILayout.EndVertical();

            EditorGUILayout.Space(10);

            // Clear Section
            EditorGUILayout.LabelField("Clear Database", EditorStyles.boldLabel);
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            {
                EditorGUILayout.HelpBox(
                    "⚠️ WARNING: Clearing the private database will delete your entire relationship history. " +
                    "This cannot be undone unless you have a backup!",
                    MessageType.Warning
                );

                EditorGUILayout.Space(5);

                if (!showClearConfirmation)
                {
                    if (GUILayout.Button("Clear Private Database"))
                    {
                        showClearConfirmation = true;
                    }
                }
                else
                {
                    EditorGUILayout.LabelField("Are you absolutely sure?", EditorStyles.boldLabel);
                    EditorGUILayout.BeginHorizontal();
                    {
                        if (GUILayout.Button("Yes, Clear Database", GUILayout.Height(30)))
                        {
                            ClearPrivateDatabase();
                            showClearConfirmation = false;
                        }

                        if (GUILayout.Button("Cancel", GUILayout.Height(30)))
                        {
                            showClearConfirmation = false;
                        }
                    }
                    EditorGUILayout.EndHorizontal();
                }
            }
            EditorGUILayout.EndVertical();
        }

        #endregion

        #region Stats Tab

        private void DrawStatsTab()
        {
            var manager = SynthesisManager.Instance;

            if (manager == null)
            {
                EditorGUILayout.HelpBox("SynthesisManager not found in scene.", MessageType.Warning);
                return;
            }

            EditorGUILayout.LabelField("Detailed Statistics", EditorStyles.boldLabel);
            EditorGUILayout.Space(5);

            var stats = manager.GetStats();

            // Full stats display
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            {
                EditorGUILayout.LabelField("Integration Statistics", EditorStyles.boldLabel);
                EditorGUILayout.Space(3);
                EditorGUILayout.TextArea(stats.ToString(), GUILayout.Height(150));
            }
            EditorGUILayout.EndVertical();

            EditorGUILayout.Space(10);

            // Additional info
            EditorGUILayout.LabelField("System Info", EditorStyles.boldLabel);
            DrawStatSection("Runtime", new Dictionary<string, string>
            {
                { "Unity Version", Application.unityVersion },
                { "Platform", Application.platform.ToString() },
                { "Play Mode", EditorApplication.isPlaying ? "Playing" : "Stopped" }
            });
        }

        #endregion

        #region Actions

        private void ConnectToServer()
        {
            var manager = SynthesisManager.Instance;
            if (manager != null)
            {
                manager.Connect();
                Debug.Log("[SynthesisProWindow] Connecting to server...");
            }
            else
            {
                Debug.LogError("[SynthesisProWindow] SynthesisManager not found!");
            }
        }

        private void DisconnectFromServer()
        {
            var manager = SynthesisManager.Instance;
            if (manager != null)
            {
                manager.Disconnect();
                Debug.Log("[SynthesisProWindow] Disconnected from server");
            }
        }

        private void SendPing()
        {
            var manager = SynthesisManager.Instance;
            if (manager != null && manager.IsConnected)
            {
                manager.SendCommand(new BridgeCommand
                {
                    id = $"ping_{System.DateTime.Now.Ticks}",
                    type = "ping",
                    parameters = new Dictionary<string, object>()
                });
                Debug.Log("[SynthesisProWindow] Ping sent");
            }
        }

        private void SendChatMessage()
        {
            var manager = SynthesisManager.Instance;
            if (manager != null && manager.IsConnected && !string.IsNullOrWhiteSpace(chatMessage))
            {
                // Add to history
                chatHistory.Add(new ChatMessage
                {
                    Message = chatMessage,
                    IsUser = true,
                    Timestamp = System.DateTime.Now.ToString("HH:mm:ss")
                });

                // Send to server
                manager.SendChatMessage(chatMessage, chatContext);

                Debug.Log($"[SynthesisProWindow] Chat message sent: {chatMessage}");

                // Clear input
                chatMessage = "";
                chatContext = "";

                // Scroll to bottom
                chatScrollPosition = new Vector2(0, float.MaxValue);
            }
        }

        private void SearchKnowledge()
        {
            var manager = SynthesisManager.Instance;
            if (manager != null && manager.IsConnected && !string.IsNullOrWhiteSpace(searchQuery))
            {
                manager.SearchKnowledge(searchQuery, searchTopK, searchPrivate);
                Debug.Log($"[SynthesisProWindow] Search query sent: {searchQuery}");

                // Clear previous results (will be populated when server responds)
                searchResults.Clear();

                // TODO: Subscribe to result callback to populate searchResults
            }
        }

        private void CreateSynthesisManager()
        {
            var go = new GameObject("SynthesisManager");
            go.AddComponent<SynthesisManager>();
            Selection.activeGameObject = go;
            Debug.Log("[SynthesisProWindow] Created SynthesisManager");
        }

        private void BackupPrivateDatabase()
        {
            var manager = SynthesisManager.Instance;
            if (manager != null && manager.IsConnected)
            {
                manager.SendCommand(new BridgeCommand
                {
                    id = $"backup_db_{System.DateTime.Now.Ticks}",
                    type = "backup_private_db",
                    parameters = new Dictionary<string, object>()
                });
                Debug.Log("[SynthesisProWindow] Backup command sent");
                EditorUtility.DisplayDialog("Backup", "Backup command sent to server. Check console for result.", "OK");
            }
        }

        private void ClearPrivateDatabase()
        {
            var manager = SynthesisManager.Instance;
            if (manager != null && manager.IsConnected)
            {
                manager.SendCommand(new BridgeCommand
                {
                    id = $"clear_db_{System.DateTime.Now.Ticks}",
                    type = "clear_private_db",
                    parameters = new Dictionary<string, object>
                    {
                        { "confirm", true }
                    }
                });
                Debug.LogWarning("[SynthesisProWindow] Clear database command sent");
                EditorUtility.DisplayDialog("Clear Database", "Clear command sent to server. Your private database will be deleted.", "OK");
            }
        }

        private void RestorePrivateDatabase(string backupFilename)
        {
            var manager = SynthesisManager.Instance;
            if (manager != null && manager.IsConnected)
            {
                manager.SendCommand(new BridgeCommand
                {
                    id = $"restore_db_{System.DateTime.Now.Ticks}",
                    type = "restore_private_db",
                    parameters = new Dictionary<string, object>
                    {
                        { "backup_file", backupFilename }
                    }
                });
                Debug.Log($"[SynthesisProWindow] Restore command sent for: {backupFilename}");
                EditorUtility.DisplayDialog("Restore", $"Restore command sent for '{backupFilename}'. Check console for result.", "OK");
            }
        }

        private void RefreshBackupsList()
        {
            var manager = SynthesisManager.Instance;
            if (manager != null && manager.IsConnected)
            {
                manager.SendCommand(new BridgeCommand
                {
                    id = $"list_backups_{System.DateTime.Now.Ticks}",
                    type = "list_backups",
                    parameters = new Dictionary<string, object>()
                });
                Debug.Log("[SynthesisProWindow] List backups command sent");

                // TODO: Subscribe to result callback to populate backupsList
                // For now, this is a placeholder - Phase 3 will add proper result handling
            }
        }

        #endregion

        #region Helpers

        private string FormatUptime(double seconds)
        {
            var timespan = System.TimeSpan.FromSeconds(seconds);
            if (timespan.TotalHours >= 1)
                return $"{(int)timespan.TotalHours}h {timespan.Minutes}m";
            if (timespan.TotalMinutes >= 1)
                return $"{(int)timespan.TotalMinutes}m {timespan.Seconds}s";
            return $"{(int)timespan.TotalSeconds}s";
        }

        private string FormatBytes(long bytes)
        {
            string[] sizes = { "B", "KB", "MB", "GB" };
            double len = bytes;
            int order = 0;
            while (len >= 1024 && order < sizes.Length - 1)
            {
                order++;
                len = len / 1024;
            }
            return $"{len:0.##} {sizes[order]}";
        }

        #endregion

        #region Data Structures

        private class ChatMessage
        {
            public string Message;
            public bool IsUser;
            public string Timestamp;
        }

        private class SearchResult
        {
            public string Title;
            public string Content;
            public float Score;
        }

        private class BackupInfo
        {
            public string Filename;
            public long Size;
            public string Modified;
            public string Path;
        }

        #endregion
    }
}
