# Network Card (NIC)

> **CLI class:** `network`
> **WMI source:** `Win32_NetworkAdapter`
> **Hardware class:** `NetworkCard`
> **Tree position:** Child of `Pci` — leaf node (no children)
> **Generated:** 2026-05-20

## Overview

Represents physical network interface cards. The query is filtered to exclude virtual/loopback adapters. The filtering strategy differs based on the Windows 10 version: newer builds (≥ 10.0.18362) use the `PhysicalAdapter=True` flag; older builds filter out adapters whose `PNPDeviceID` contains `"ROOT"`.

## Fields Collected

| WMI Property | Hardware Field | Description |
|---|---|---|
| `Description` | `product` | NIC description (e.g. `"Intel(R) Ethernet Connection I219-V"`) |
| `Manufacturer` | `vendor` | NIC manufacturer |
| `MACAddress` | `serial` | MAC address (e.g. `"00:1A:2B:3C:4D:5E"`) |
| `NetConnectionID` | `logicalname` | Connection name (e.g. `"Ethernet"`, `"Wi-Fi"`) |
| `PNPDeviceID` | `pnpdeviceid` | PnP identifier |
| `Autosense` | `configuration.autonegotiation` + `capabilities.autonegotiation` | Boolean for auto-negotiation support |
| `Speed` | `configuration.speed` | Link speed in bits per second |

Collected but not mapped to any field: `Speed` (mapped to config), `SystemCreationClassName`, `AdapterType`, `Caption`, `ProductName`.

## Fixed Fields

| Field | Value |
|-------|-------|
| `id` | `"network"` |
| `class` | `"network"` |
| `claimed` | `true` |
| `description` | `"Ethernet interface"` |
| `units` | `"bit/s"` |
| `size` | `0` |
| `capacity` | `0` |
| `width` | `0` |
| `clock` | `0` |
| `businfo` | `""` |
| `version` | `""` |

## Configuration Keys

| Key | Source | Notes |
|-----|--------|-------|
| `autonegotiation` | `Autosense` WMI property | Boolean value |
| `broadcast` | `""` | Always empty |
| `driver` | `""` | Always empty |
| `driverversion` | `""` | Always empty |
| `duplex` | `""` | Always empty |
| `firmware` | `""` | Always empty |
| `ip` | `""` | Always empty |
| `latency` | `""` | Always empty |
| `link` | `""` | Always empty |
| `multicast` | `""` | Always empty |
| `port` | `""` | Always empty |
| `speed` | `Speed` WMI property | Current/max speed in bps |

## Capabilities Keys

| Key | Notes |
|-----|-------|
| `pm`, `vpd`, `msi`, `pciexpress`, `bus_master`, `cap_list` | Always empty placeholders |
| `ethernet` | Always `true` |
| `physical` | Always empty |
| `tp`, `10bt`, `10bt-fd`, `100bt`, `100bt-fd`, `1000bt`, `1000bt-fd` | Always empty |
| `autonegotiation` | Set from `Autosense` WMI property |

## WQL Filter Logic

```python
# Windows 10 < 10.0.18362
WHERE (NOT PNPDeviceID LIKE "%ROOT%")

# Windows 10 >= 10.0.18362
WHERE (PhysicalAdapter=True)
```

The version check uses `platform.release()` and `platform.version()`.

## Output Schema

```json
{
  "id": "network",
  "class": "network",
  "claimed": true,
  "description": "Ethernet interface",
  "product": "Intel(R) Ethernet Connection I219-V",
  "vendor": "Intel Corporation",
  "serial": "00:1A:2B:3C:4D:5E",
  "logicalname": "Ethernet",
  "pnpdeviceid": "PCI\\VEN_8086&DEV_15B8&...",
  "units": "bit/s",
  "configuration": {
    "autonegotiation": true,
    "speed": 1000000000
  },
  "capabilities": {
    "ethernet": true,
    "autonegotiation": true
  }
}
```

## Interactions

### Full Scan / Single Class Query

- **Trigger:** `lshw` or `lshw --class-hw network`
- **Override:** This class overrides `get_hardware()` (instead of using `wmi_method`) to apply the version-conditional `WHERE` clause via `build_wql_select()`.
- **On WMI failure:** Exits with error code `14`.

## Business Rules

- The MAC address is stored in `serial`, not a dedicated field.
- Most capability and configuration keys are empty placeholders for lshw format compatibility. Only `autonegotiation` and `speed` carry real data.
- WiFi adapters are included when they are physical adapters (pass the `PhysicalAdapter=True` or ROOT filter).

## Relationships

- **Parent:** `Pci`
- **No children.**
