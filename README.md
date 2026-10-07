# Zabbix-Based Server Health Monitoring & Real-Time Alerting Platform

An enterprise-grade Server Health Monitoring Platform built on top of **Zabbix** as the core metric and trigger engine, featuring a high-performance **FastAPI** backend, real-time **WebSocket telemetry streaming**, and a modern NOC-style **React + TypeScript** dashboard.

---

## Key Features

- **Zabbix Core Integration**: Dedicated `ZabbixService` JSON-RPC abstraction layer with circuit-breaker protection, host synchronization, and historical metric queries.
- **Deterministic Health Priority Algorithm**:
  $$\text{DOWN} \succ \text{CRITICAL} \succ \text{WARNING} \succ \text{INFO} \succ \text{HEALTHY}$$
- **Stateful Alert State Machine & Deduplication**:
  - Deterministic deduplication key: `server_id:component_type:component_id:problem_type`
  - Zero repeated emails for existing active breaches
  - Automatic escalation tracking (`WARNING` $\rightarrow$ `CRITICAL`)
  - Automatic recovery detection & recovery notifications with duration tracking
- **Generic SMTP Email Dispatcher**: Full HTML/Plaintext templates for problem and recovery notifications with exponential retry logging.
- **Dynamic Hardware Subsystem Tree**: CPU, RAM DIMMs, PSUs, Fans, RAID controllers, and Temperature sensors with strict **Zero Fake Data** enforcement (`UNSUPPORTED` / `Not Available` for unexposed sensors).
- **Maintenance Windows**: Scheduled alert suppression periods.
- **Audit Logging & RBAC**: `ADMIN`, `OPERATOR`, and `VIEWER` roles with complete audit trail.

---

## Directory Layout

```text
Server Health Monitoring/
├── backend/                  # FastAPI Application, Services, Models, Schemas
│   ├── app/
│   │   ├── api/              # REST Endpoints (Auth, Servers, Alerts, Dashboard, Maintenance)
│   │   ├── core/             # Configuration, Database, Security, Structured Logging
│   │   ├── models/           # SQLAlchemy ORM Models
│   │   ├── schemas/          # Pydantic Schemas & DTOs
│   │   ├── services/         # Zabbix Client, Alert State Machine, SMTP, Hardware Provider
│   │   ├── websocket/        # Real-time WebSocket Hub
│   │   └── main.py           # FastAPI Master App
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                 # React + TypeScript + Vite + TailwindCSS
│   ├── src/
│   │   ├── components/       # Navbar, Sidebar, HealthBadge
│   │   ├── pages/            # Dashboard, Servers, ServerDetails, Alerts, Maintenance, Settings
│   │   ├── services/         # Axios API client
│   │   ├── hooks/            # Reconnecting WebSocket hook
│   │   └── types/            # TypeScript Interface definitions
│   ├── Dockerfile
│   └── package.json
├── database/                 # Database seed script & schemas
├── deployment/               # Agent installers (Windows PowerShell & Linux Bash)
├── docs/                     # Architecture & Deployment Guide
├── tests/                    # Pytest unit & integration test suite
├── docker-compose.yml        # Docker deployment stack
└── README.md
```

---

## Running the Platform

### 1. Seed Initial Baseline
```bash
python database/seed_demo_data.py
```

### 2. Launch Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
- API Docs: `http://localhost:8000/docs`

### 3. Launch Frontend
```bash
cd frontend
npm.cmd run dev
```
- Web UI: `http://localhost:5173`
- Default Login: `admin` / `admin123`

### 4. Running Unit Tests
```bash
python -m pytest tests/unit
```
