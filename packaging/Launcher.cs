using System;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;
using System.Reflection;
[assembly: AssemblyTitle("Omni Voice")]
[assembly: AssemblyVersion("1.0.0.0")]
internal static class Launcher {
    [STAThread] static int Main(string[] args) {
        try {
            string root = AppDomain.CurrentDomain.BaseDirectory;
            string python = Path.Combine(root, "_runtime", "pythonw.exe");
            var info = new ProcessStartInfo(python);
            info.UseShellExecute = false;
            info.CreateNoWindow = true;
            info.WorkingDirectory = root;
            info.Arguments = "-I -X utf8 \"" + Path.Combine(root, "bootstrap.py") + "\"";
            foreach (string arg in args) {
                if (arg.Contains("\"")) throw new ArgumentException("Invalid argument");
                info.Arguments += " \"" + arg + "\"";
            }
            info.EnvironmentVariables["OMNI_INSTALLED"] = "1";
            info.EnvironmentVariables.Remove("PYTHONHOME");
            info.EnvironmentVariables.Remove("PYTHONPATH");
            info.EnvironmentVariables["PATH"] = Path.Combine(root,"bin") + ";" +
                Path.Combine(root,"_runtime") + ";" + Environment.GetFolderPath(Environment.SpecialFolder.System);
            using (var process = Process.Start(info)) { process.WaitForExit(); return process.ExitCode; }
        } catch (Exception e) {
            MessageBox.Show("Không mở được Omni Voice.\n" + e.Message, "Omni Voice", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        }
    }
}
