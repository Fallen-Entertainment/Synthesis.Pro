using UnityEditor;
using UnityEngine;
using System.IO;
using System.Linq;

namespace Synthesis.Editor
{
    /// <summary>
    /// Exports Synthesis.Pro as a Unity package for distribution
    /// Called by GitHub Actions for automated releases
    /// </summary>
    public static class ExportPackage
    {
        // Runtime dependencies excluded from package (downloaded via FirstTimeSetup)
        private static readonly string[] EXCLUDED_PATHS = new string[]
        {
            "Assets/Synthesis.Pro/KnowledgeBase/python",
            "Assets/Synthesis.Pro/Server/node",
            "Assets/Synthesis.Pro/Server/models",
            "Assets/Synthesis.Pro/Server/synthesis_private.db",
            "Assets/Synthesis.Pro/Server/synthesis_knowledge.db",
            "Assets/Synthesis.Pro/Server/synthesis_public.db"
        };

        [MenuItem("Tools/Synthesis/Export Package")]
        public static void Export()
        {
            string packageName = "Synthesis.Pro.unitypackage";

            // Get all assets to export with exclusions
            var assetPaths = GetFilteredAssetPaths();

            if (assetPaths.Length == 0)
            {
                Debug.LogError("[Export] No valid asset paths found to export!");
                return;
            }

            // Export flags
            ExportPackageOptions options =
                ExportPackageOptions.Recurse |
                ExportPackageOptions.IncludeDependencies;

            Debug.Log($"[Export] Creating package: {packageName}");
            Debug.Log($"[Export] Exporting {assetPaths.Length} assets");
            Debug.Log($"[Export] Excluded: {string.Join(", ", EXCLUDED_PATHS.Where(p => Directory.Exists(p) || File.Exists(p)))}");

            // Export the package
            AssetDatabase.ExportPackage(
                assetPaths,
                packageName,
                options
            );

            Debug.Log($"[Export] ✅ Package created successfully: {packageName}");

            // Show in file explorer
            EditorUtility.RevealInFinder(Path.GetFullPath(packageName));
        }

        /// <summary>
        /// Gets all asset paths with exclusions applied
        /// </summary>
        private static string[] GetFilteredAssetPaths()
        {
            var allPaths = new System.Collections.Generic.List<string>();

            // Start with main folders
            string[] rootPaths = new string[]
            {
                "Assets/Synthesis.Pro",
                "Assets/Synthesis_AI" // Legacy name support
            };

            foreach (var rootPath in rootPaths)
            {
                if (!AssetDatabase.IsValidFolder(rootPath))
                    continue;

                // Get all assets in this folder
                string[] guids = AssetDatabase.FindAssets("", new[] { rootPath });
                foreach (string guid in guids)
                {
                    string path = AssetDatabase.GUIDToAssetPath(guid);

                    // Check if this path should be excluded
                    bool shouldExclude = false;
                    foreach (string excludedPath in EXCLUDED_PATHS)
                    {
                        if (path.StartsWith(excludedPath))
                        {
                            shouldExclude = true;
                            break;
                        }
                    }

                    if (!shouldExclude)
                    {
                        allPaths.Add(path);
                    }
                }
            }

            return allPaths.Distinct().ToArray();
        }

        /// <summary>
        /// Export method for CI/CD (no UI interactions)
        /// </summary>
        public static void ExportCI()
        {
            string packageName = "Synthesis.Pro.unitypackage";

            // Get all assets to export with exclusions
            var assetPaths = GetFilteredAssetPaths();

            if (assetPaths.Length == 0)
            {
                Debug.LogError("[Export CI] No valid asset paths found!");
                EditorApplication.Exit(1);
                return;
            }

            ExportPackageOptions options =
                ExportPackageOptions.Recurse |
                ExportPackageOptions.IncludeDependencies;

            Debug.Log($"[Export CI] Exporting {packageName}...");
            Debug.Log($"[Export CI] Exporting {assetPaths.Length} assets");

            try
            {
                AssetDatabase.ExportPackage(
                    assetPaths,
                    packageName,
                    options
                );

                Debug.Log($"[Export CI] ✅ Success: {packageName}");
                EditorApplication.Exit(0);
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[Export CI] ❌ Failed: {e.Message}");
                EditorApplication.Exit(1);
            }
        }
    }
}
