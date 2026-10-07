# Hardware Monitoring & Zero-Fake-Data Enforcement Guide

## 1. Zero-Fake-Data Policy
In accordance with production SRE standards, this platform **strictly prohibits fabricating artificial PSU, Fan, RAID, or Temperature data**. 
If a host (such as a laptop VM or cloud instance) does not expose IPMI / BMC / Redfish sensors, the subsystem is explicitly flagged as `UNSUPPORTED` with data source `OS`.

```text
Component: Chassis Power Supply
Status:    UNSUPPORTED
Message:   Sensor not available on client OS / Hypervisor
Source:    OS
```

## 2. Dynamic Hardware Hierarchy
When connected to physical hardware with BMC / IPMI 2.0 / SNMP / Redfish support, the `HardwareProvider` dynamically populates:

```text
SERVER-01
├── CPU
│   ├── CPU 0
│   └── CPU 1
├── Memory
│   ├── DIMM A1
│   └── DIMM B1
├── Storage & RAID
│   ├── RAID Controller 1 (MegaRAID / PERC)
│   │   ├── Disk 0 (Online / Healthy)
│   │   └── Disk 1 (Online / Healthy)
├── Power Supplies
│   ├── PSU 1 (Healthy, 230V, 120W)
│   └── PSU 2 (Healthy, 230V, 118W)
├── Cooling Fans
│   ├── Fan 1 (4200 RPM, OK)
│   └── Fan 2 (4300 RPM, OK)
└── Temperature Sensors
    ├── CPU Package Temp (48.5 °C)
    └── Inlet Ambient Temp (22.0 °C)
```

## 3. Supported Sensor Protocols
- **Zabbix Agent 2**: OS-level counters, SMART drive metrics, storage filesystems.
- **IPMI 2.0**: Chassis sensors, PSU redundancy, fan tachometers, thermal zones.
- **SNMP v2c / v3**: Network switches, RAID controller traps, PDU power metrics.
- **Redfish REST API**: Modern Dell iDRAC9, HPE iLO5/6, Lenovo XClarity telemetry.
