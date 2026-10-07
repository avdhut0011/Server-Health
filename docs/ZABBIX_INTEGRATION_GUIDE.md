# Zabbix Integration & API Guide

## 1. Zabbix JSON-RPC 2.0 Client

The custom backend integrates with Zabbix through `ZabbixService`:
- **Protocol**: JSON-RPC 2.0 over HTTP/HTTPS
- **Authentication**: Supports both username/password session tokens (`user.login`) and long-lived API tokens (`Authorization: Bearer <token>`).
- **Resilience**: Integrated **Circuit Breaker** prevents cascading failures when Zabbix server is rebooting or under maintenance.

## 2. Monitored Metrics Extracted from Zabbix

| Subsystem | Zabbix Item Keys | Target Metric |
|---|---|---|
| **CPU** | `system.cpu.util`, `perf_counter["\Processor(_Total)\% Processor Time"]` | CPU Utilization (%) |
| **RAM** | `vm.memory.util`, `vm.memory.size[pused]`, `vm.memory.size[pavailable]` | RAM Utilization (%) |
| **Storage** | `vfs.fs.size[*,pused]`, `vfs.fs.dependent.size[*,pused]` | Filesystem Utilization (%) |
| **Uptime** | `system.uptime` | System Uptime (seconds) |
| **Network** | `net.if.in[*]`, `net.if.out[*]`, `icmppingsec`, `icmppingloss` | Latency (ms) & Packet Loss (%) |
| **Services** | `service.info[*]`, `systemd.unit.info[*]` | Service Run State |

## 3. Host Discovery & Problem Sync

The background worker queries:
```json
{
  "jsonrpc": "2.0",
  "method": "problem.get",
  "params": {
    "output": "extend",
    "recent": "true",
    "sortfield": ["eventid"],
    "sortorder": "DESC"
  },
  "auth": "<token>",
  "id": 101
}
```
Problems are mapped directly into the custom alert state machine.
