$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path $PSScriptRoot -Parent
$taskReportRoot = Join-Path $taskRoot '_qa\packaging'
$taskInstallDir = [IO.Path]::GetFullPath((Join-Path $env:TEMP 'OmniVoice-Install-QA-20261010'))
$taskTempRoot = [IO.Path]::GetFullPath($env:TEMP).TrimEnd('\') + '\'
if (-not $taskInstallDir.StartsWith($taskTempRoot,[StringComparison]::OrdinalIgnoreCase)) { throw 'Invalid QA target' }
if (Test-Path -LiteralPath $taskInstallDir) { throw 'QA target already exists; inspect before reusing' }
$taskUninstallKey='HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\{6B0C6F64-41B4-4DC3-AE98-6CA25CB9B8B0}_is1'
if (Test-Path $taskUninstallKey) { throw 'An existing Omni Voice installation is registered; preserve it' }
$taskSetup=Join-Path $taskRoot 'release\OmniVoice-Setup-1.0.0.exe'
$taskLog=Join-Path $taskReportRoot 'install.log'
New-Item -ItemType Directory -Path $taskReportRoot -Force | Out-Null
$taskInstall=Start-Process -FilePath $taskSetup -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/NOICONS','/MERGETASKS="!desktopicon"',('/DIR="'+$taskInstallDir+'"'),('/LOG="'+$taskLog+'"')) -WindowStyle Hidden -PassThru -Wait
if ($taskInstall.ExitCode -ne 0) { throw ('Installer failed: '+$taskInstall.ExitCode) }
Write-Output ('INSTALLED '+$taskInstallDir)
$taskPsi=New-Object Diagnostics.ProcessStartInfo
$taskPsi.FileName=Join-Path $taskInstallDir 'OmniVoice.exe'
$taskPsi.WorkingDirectory=$env:WINDIR
$taskPsi.UseShellExecute=$false
$taskPsi.CreateNoWindow=$true
$taskPsi.Arguments='--self-test "'+(Join-Path $taskReportRoot 'installed-report.json')+'"'
$taskPsi.EnvironmentVariables['LOCALAPPDATA']=Join-Path $taskReportRoot 'profile-installed'
$taskPsi.EnvironmentVariables['PYTHONPATH']='Z:\unavailable-python'
$taskPsi.EnvironmentVariables['PYTHONHOME']='Z:\unavailable-python'
$taskExe=New-Object Diagnostics.Process
$taskExe.StartInfo=$taskPsi
$taskExe.Start() | Out-Null
$taskExe.WaitForExit()
if ($taskExe.ExitCode -ne 0) { throw ('Installed app self-test failed: '+$taskExe.ExitCode) }
Write-Output 'INSTALLED APP TEST PASSED'
$taskUninstall=Join-Path $taskInstallDir 'unins000.exe'
if (-not (Test-Path -LiteralPath $taskUninstall)) { throw 'Uninstaller missing' }
$taskRemove=Start-Process -FilePath $taskUninstall -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART',('/LOG="'+(Join-Path $taskReportRoot 'uninstall.log')+'"')) -WindowStyle Hidden -PassThru -Wait
if ($taskRemove.ExitCode -ne 0) { throw ('Uninstaller failed: '+$taskRemove.ExitCode) }
if (Test-Path -LiteralPath (Join-Path $taskInstallDir 'OmniVoice.exe')) { throw 'Executable still installed' }
if (Test-Path -LiteralPath (Join-Path $taskInstallDir 'data\models')) { throw 'Model still installed' }
if (Test-Path $taskUninstallKey) { throw 'Uninstall entry not removed' }
@{install_exit=0;self_test_exit=0;uninstall_exit=0;test_directory=$taskInstallDir;model_removed=$true;registry_removed=$true} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskReportRoot 'installer-report.json') -Encoding utf8
Write-Output 'INSTALL / OFFLINE GENERATION / UNINSTALL PASSED'
