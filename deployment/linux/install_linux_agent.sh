#!/usr/bin/env bash
# ==============================================================================
# Zabbix Agent 2 Linux (Debian/Ubuntu/RHEL) Automated Deployment Script
# ==============================================================================

set -e

ZABBIX_SERVER_IP="${1:-192.168.56.101}"
HOSTNAME_OVERRIDE="${2:-$(hostname)}"

echo "===================================================="
echo "Zabbix Agent 2 Linux Deployment Script"
echo "Target Zabbix Server IP: ${ZABBIX_SERVER_IP}"
echo "Monitored Hostname:      ${HOSTNAME_OVERRIDE}"
echo "===================================================="

# Check root
if [ "$EUID" -ne 0 ]; then
  echo "[ERROR] Please run as root (sudo bash install_linux_agent.sh)"
  exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
  . /etc/os-release
  OS=$ID
  VERSION=$VERSION_ID
else
  echo "[ERROR] Cannot identify OS distribution."
  exit 1
fi

echo "[1/4] Installing Zabbix repository and agent..."
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
  apt-get update
  apt-get install -y zabbix-agent2 zabbix-agent2-plugin-* || apt-get install -y zabbix-agent
elif [ "$OS" = "rhel" ] || [ "$OS" = "centos" ] || [ "$OS" = "rocky" ] || [ "$OS" = "almalinux" ]; then
  dnf install -y zabbix-agent2 || yum install -y zabbix-agent2
fi

CONF_FILE="/etc/zabbix/zabbix_agent2.conf"
if [ ! -f "$CONF_FILE" ]; then
  CONF_FILE="/etc/zabbix/zabbix_agentd.conf"
fi

echo "[2/4] Configuring ${CONF_FILE}..."
sed -i "s/^Server=.*/Server=${ZABBIX_SERVER_IP}/" "$CONF_FILE"
sed -i "s/^ServerActive=.*/ServerActive=${ZABBIX_SERVER_IP}/" "$CONF_FILE"
sed -i "s/^Hostname=.*/Hostname=${HOSTNAME_OVERRIDE}/" "$CONF_FILE"

echo "[3/4] Enabling and starting zabbix-agent service..."
systemctl restart zabbix-agent2 2>/dev/null || systemctl restart zabbix-agent
systemctl enable zabbix-agent2 2>/dev/null || systemctl enable zabbix-agent

echo "[4/4] Verifying agent status..."
systemctl is-active zabbix-agent2 2>/dev/null || systemctl is-active zabbix-agent

echo "===================================================="
echo "Linux Agent Setup Complete and Running!"
echo "===================================================="
