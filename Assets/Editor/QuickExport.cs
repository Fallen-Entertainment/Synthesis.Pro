using UnityEditor;
using UnityEngine;
using System.IO;
using System.Linq;

public static class QuickExport
{
    // Runtime dependencies excluded from package
    private static readonly string[] EXCLUDED_FOLDERS = new string[]
    {
        "python",
        "node",
        "models"
    };

    private static readonly string[] EXCLUDED_FILES = new string[]
    {
        "synthesis_private.db",
        "synthesis_knowledge.db",
        "synthesis_public.db"
    };

    private static readonly string[] WINDOWS_RESERVED = new string[]
    {
        "CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
    };

    public static void Export()
    {
        string packageName = "Synthesis.Pro.unitypackage";
        string sourceFolder = Path.Combine(Application.dataPath, "Synthesis.Pro");
        string tempFolder = Path.Combine(Application.dataPath, "Synthesis.Pro_Export");

        if (!Directory.Exists(sourceFolder))
        {
            Debug.LogError($"[Export] Source folder not found: {sourceFolder}");
            EditorApplication.Exit(1);
            return;
        }

        try
        {
            Debug.Log("[Export] Creating filtered copy for export...");

            // Create filtered copy, excluding runtime deps
            CopyDirectoryFiltered(sourceFolder, tempFolder);

            // Refresh so Unity sees the new files
            AssetDatabase.Refresh();

            Debug.Log($"[Export] Creating package: {packageName}");

            // Export the filtered package
            AssetDatabase.ExportPackage(
                "Assets/Synthesis.Pro_Export",
                packageName,
                ExportPackageOptions.Recurse
            );

            Debug.Log($"[Export] Package created successfully: {packageName}");
        }
        catch (System.Exception e)
        {
            Debug.LogError($"[Export] Failed: {e.Message}");
            EditorApplication.Exit(1);
        }
        finally
        {
            // Clean up - remove temporary export folder
            if (Directory.Exists(tempFolder))
            {
                Debug.Log("[Export] Cleaning up temporary files...");
                Directory.Delete(tempFolder, true);
                File.Delete(tempFolder + ".meta");
                AssetDatabase.Refresh();
            }

            EditorApplication.Exit(0);
        }
    }

    private static void CopyDirectoryFiltered(string sourcePath, string targetPath)
    {
        Directory.CreateDirectory(targetPath);

        // Copy files
        foreach (string file in Directory.GetFiles(sourcePath))
        {
            string fileName = Path.GetFileName(file);
            string fileNameUpper = fileName.ToUpperInvariant();
            string fileNameNoExt = Path.GetFileNameWithoutExtension(fileName).ToUpperInvariant();

            // Skip Windows reserved filenames
            if (WINDOWS_RESERVED.Contains(fileNameUpper) || WINDOWS_RESERVED.Contains(fileNameNoExt))
            {
                Debug.Log($"[Export] Excluding Windows reserved file: {fileName}");
                continue;
            }

            // Skip excluded files
            if (EXCLUDED_FILES.Any(excluded => fileName.Contains(excluded)))
            {
                Debug.Log($"[Export] Excluding file: {fileName}");
                continue;
            }

            string targetFile = Path.Combine(targetPath, fileName);
            File.Copy(file, targetFile, true);
        }

        // Copy subdirectories recursively
        foreach (string directory in Directory.GetDirectories(sourcePath))
        {
            string dirName = Path.GetFileName(directory);

            // Skip excluded folders
            if (EXCLUDED_FOLDERS.Contains(dirName))
            {
                Debug.Log($"[Export] Excluding folder: {dirName}");
                continue;
            }

            string targetDir = Path.Combine(targetPath, dirName);
            CopyDirectoryFiltered(directory, targetDir);
        }
    }
}
