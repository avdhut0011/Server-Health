# Server Health Monitoring Platform - Troubleshooting Guide

## Common Issues & Resolutions

### 1. Zabbix API Connection Failed
- **Symptom**: Settings page shows `DISCONNECTED / MOCK` or `Zabbix Connection Error`.
- **Resolution**:
  - Verify Zabbix Server is running: `curl http://<zabbix-host>:8080/api_jsonrpc.php`
  - Ensure correct credentials in `.env` (`ZABBIX_USERNAME=Admin`, `ZABBIX_PASSWORD=zabbix`).
  - Verify firewall on Linux VM allows incoming HTTP traffic on port 8080.

### 2. Monitored Server Shows Offline (Consecutive Failures)
- **Symptom**: Node health transitions to `DOWN` with 3 failed checks.
- **Resolution**:
  - Check if Zabbix Agent 2 service is running on the target node:
    - Windows: `Get-Service "Zabbix Agent 2"`
    - Linux: `sudo systemctl status zabbix-agent2`
  - Verify port 10050 is open: `Test-NetConnection -ComputerName <ip> -Port 10050`
  - Verify `zabbix_agent2.conf` specifies `Server=<zabbix-server-ip>`.

### 3. SMTP Test Email Fails
- **Symptom**: `Failed to dispatch test email via SMTP`.
- **Resolution**:
  - Verify SMTP host and port in `.env` or Settings.
  - If testing locally without an external SMTP provider, run the bundled Mailhog container (`docker-compose up mailhog`) which listens on port 1025.
  - Check `backend/logs/notification.log` for detailed transmission errors.

### 4. WebSocket Disconnects
- **Symptom**: Dashboard shows `WS Live: Reconnecting`.
- **Resolution**:
  - The client automatically retries every 3 seconds.
  - If behind Nginx or reverse proxy, ensure `Upgrade` and `Connection "Upgrade"` headers are forwarded.
