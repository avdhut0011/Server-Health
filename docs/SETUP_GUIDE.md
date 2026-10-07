# Server Health Monitoring Platform - Deployment & Operations Guide

## 1. Architecture Overview
This platform provides centralized NOC telemetry, server inventory tracking, deduplicated stateful alerting, and dynamic hardware status on top of a core **Zabbix Server 7.0 LTS** engine.

```text
Host: Windows 11 Laptop
   |
   +--> React + TypeScript Vite Frontend (Port 5173 / Port 80)
   +--> FastAPI Python 3.12+ Backend (Port 8000)
   +--> Custom PostgreSQL Database (Port 5432)
   |
   +--> Linux VM (e.g. Ubuntu 24.04 via Hyper-V/VMware/VirtualBox)
           |
           +--> Zabbix Server & Web Frontend (Port 8080)
           +--> Zabbix Database
           +--> Zabbix Agent 2 (Linux VM Node)
```

---

## 2. Quick Start Options

### Option A: Local Development Run (Fastest)

1. **Seed Baseline Data**:
   ```bash
   python database/seed_demo_data.py
   ```
   This creates initial demo nodes (`Windows 11 Host` and `Linux VM`), default roles (`ADMIN`, `OPERATOR`, `VIEWER`), and the administrator account (`admin` / `admin123`).

2. **Start Backend**:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --port 8000
   ```

3. **Start Frontend**:
   ```bash
   cd frontend
   npm.cmd run dev
   ```
   Open `http://localhost:5173` in your browser.

---

### Option B: Docker Compose Full Stack

```bash
docker-compose up -d --build
```
- Custom Web Dashboard: `http://localhost:3000`
- FastAPI REST Docs: `http://localhost:8000/docs`
- Mailhog SMTP Inspector: `http://localhost:8025`

---

## 3. Zabbix Integration Setup

1. In the Linux VM hosting Zabbix, ensure the Zabbix Web interface is accessible.
2. In the custom application `.env` or `Settings` page:
   - `ZABBIX_URL=http://<linux-vm-ip>:8080/api_jsonrpc.php`
   - `ZABBIX_USERNAME=Admin`
   - `ZABBIX_PASSWORD=zabbix`
3. Link monitored servers in the UI by setting `Zabbix Host ID` (e.g., `10084` for Linux VM).

---

## 4. Testing SRE Failure Simulations

1. **CPU Stress Test**:
   - On Windows: Run a PowerShell CPU loop.
   - On Linux: Run `stress-ng --cpu 4 --timeout 60s`.
   - Verify: Health status transitions to `WARNING` at 70%, `CRITICAL` at 90%, deduplicated alerts in Console, and instant `[RECOVERED]` email upon completion.

2. **Server Unreachability (DOWN Detection)**:
   - Block TCP port 10050 or pause the Linux VM.
   - Verify: Consecutive failures increment (1 $\rightarrow$ 2 $\rightarrow$ 3), then server transitions to `DOWN` state and generates an incident.
   - Resume VM $\rightarrow$ server transitions to `RECOVERED` with duration recorded.
