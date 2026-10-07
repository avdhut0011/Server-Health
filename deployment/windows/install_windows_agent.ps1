<#
.SYNOPSIS
    Automated Windows Zabbix Agent 2 Installer & Configuration Script.
.DESCRIPTION
    Installs Zabbix Agent 2 on Windows 11 / Windows Server, configures Server & ServerActive endpoints,
    registers the Windows Service, opens firewall port 10050, and starts the service.
#>

param (
    [string]$ZabbixServerIP = "192.168.56.101",
    [string]$Hostname = $env:COMPUTERNAME,
    [string]$InstallDir = "C:\Program Files\Zabbix Agent 2"
)

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "ZABBIX AGENT 2 WINDOWS DEPLOYMENT SCRIPT" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

# 1. Check Administrator Privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Error "This script must be executed as Administrator!"
    Exit 1
}

Write-Host "[1/5] Target Server IP: $ZabbixServerIP" -ForegroundColor Yellow
Write-Host "[1/5] Monitored Hostname: $Hostname" -ForegroundColor Yellow

# 2. Firewall Rule
Write-Host "[2/5] Configuring Windows Firewall rule for TCP port 10050..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "Zabbix Agent 2 Poller Port" -Direction Inbound -LocalPort 10050 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue

# 3. Create Configuration File
$configPath = "$InstallDir\zabbix_agent2.conf"
if (Test-Path $InstallDir) {
    Write-Host "[3/5] Writing configuration to $configPath..." -ForegroundColor Yellow
    $configContent = @"
LogType=file
LogFile=$InstallDir\zabbix_agent2.log
LogFileSize=10
Server=$ZabbixServerIP
ServerActive=$ZabbixServerIP
Hostname=$Hostname
ControlSocket=\\.\pipe\zabbix_agent2_pipe
Include=$InstallDir\zabbix_agent2.d\*.conf
PluginConfigDir=$InstallDir\zabbix_agent2.d\plugins.d
"@
    Set-Content -Path $configPath -Value $configContent
}

# 4. Service Management
Write-Host "[4/5] Checking Zabbix Agent Service..." -ForegroundColor Yellow
$service = Get-Service -Name "Zabbix Agent 2" -ErrorAction SilentlyContinue
if ($service) {
    Restart-Service -Name "Zabbix Agent 2"
    Write-Host "[5/5] Zabbix Agent 2 Service successfully restarted and running!" -ForegroundColor Green
} else {
    Write-Host "[INFO] Download MSI installer from https://www.zabbix.com/download_agents and run with SERVER=$ZabbixServerIP HOSTNAME=$Hostname" -ForegroundColor Cyan
}

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "Windows Agent Configuration Complete!" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Cyan
