# Server Health Monitoring Platform - Architecture Deep Dive

## 1. System Topology & Separation of Concerns

```text
                    +--------------------------------+
                    | Modern React + TypeScript UI  |
                    | (NOC Dark Theme, ECharts, WS)  |
                    +---------------+----------------+
                                    |
                         HTTPS REST / WebSockets
                                    |
                    +---------------+----------------+
                    |    FastAPI Custom Backend      |
                    |  - Inventory & Health Engine   |
                    |  - Alert State Machine (Dedup) |
                    |  - Generic SMTP Dispatcher     |
                    |  - Hardware Provider (No-Fake) |
                    |  - Async Sync Worker           |
                    +---------------+----------------+
                                    |
                           Zabbix JSON-RPC 2.0
                                    |
                    +---------------+----------------+
                    |     Zabbix Server 7.0 LTS      |
                    |  - Native Item Poller          |
                    |  - Triggers & Event Engine     |
                    |  - Historical Trends Storage   |
                    +---------------+----------------+
                                    |
                    +---------------+----------------+
                    |   Target Monitored Nodes       |
                    |  - Windows 11 Host (Agent 2)   |
                    |  - Linux VM (Agent 2)          |
                    |  - BMC / IPMI / Redfish Nodes  |
                    +--------------------------------+
```

## 2. Health Priority Algorithm

Overall server health is evaluated deterministically using:
$$\text{DOWN} \succ \text{CRITICAL} \succ \text{WARNING} \succ \text{INFO} \succ \text{HEALTHY}$$

- **Consecutive Failures**: If an agent misses $N$ consecutive polls ($N=3$ by default), the node transitions to `DOWN`.
- **Component Propagation**: If any hardware subsystem (e.g. PSU 2 Failed) is `CRITICAL`, overall node health escalates to `CRITICAL`.

## 3. Alert State Machine & Deduplication

- Deduplication Key: `server_id:component_type:component_id:problem_type`.
- When an active incident continues breach intervals, only the trigger value and timestamp are refreshed.
- If severity escalates (e.g., `WARNING` $\rightarrow$ `CRITICAL`), an escalation event is logged and dispatched.
- Once metrics clear, the incident transitions to `RECOVERED`, computing exact incident duration and sending a recovery notification.
