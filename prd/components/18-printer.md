# Printer

> **CLI class:** `printer`
> **WMI source:** `Win32_Printer`
> **Hardware class:** `Printer`
> **Tree position:** Child of `BaseBoard`
> **Generated:** 2026-05-21

## Overview

Represents printers and print queues configured on the machine. Reports active drivers, printer ports, and identifies if the device is a local device or network share.

## Fields Collected

### From `Win32_Printer`

| WMI Property | Hardware Field | Description |
|---|---|---|
| `DeviceID` / `Name` | `id` | Printer identifier, parsed as `"printer:N"` where N is sequence |
| `Caption` / `Name` | `description` | Printable name / description |
| `DriverName` | `product` | Driver / processor name of the printer (e.g. `"HP LaserJet Professional"`) |
| `Manufacturer` / `DriverName` | `vendor` | Printer vendor (inferred from driver or name if available) |
| `PortName` | `logicalname` | Connection port (e.g. `"USB001"`, `"192.168.1.100"`) |
| `Network` | `configuration.network` | Shared connection flag (`"true"` / `"false"`) |
| `Local` | `configuration.local` | Local device flag (`"true"` / `"false"`) |

## Output Schema

```json
{
  "id": "printer:0",
  "class": "printer",
  "claimed": true,
  "handle": "",
  "description": "HP OfficeJet Pro",
  "product": "HP OfficeJet Pro K8600 PCL 3",
  "vendor": "HP",
  "logicalname": "USB001",
  "configuration": {
    "network": "false",
    "local": "true"
  }
}
```

## Interactions

### Full Scan (default invocation)

- **Trigger:** `lshw` — collected as child of `BaseBoard`
- **Behavior:** Queries print queues using `SELECT * FROM Win32_Printer` and appends `Printer` nodes to base motherboard.

### Single Class Query

- **Trigger:** `lshw --class-hw printer`
- **Behavior:** Queries printer queues only.
- **On WMI failure:** Exits with error code `18`.

## Business Rules

- Vendor extraction automatically analyzes the product name and driver details, mapping standard printer vendors like `"HP"`, `"Epson"`, `"Canon"`, `"Brother"`, `"Lexmark"`, `"Xerox"`, `"Ricoh"`, and software virtual PDF printer drivers.
- Safe `SELECT *` query pattern ensures that missing properties on custom Windows installations do not crash the enumeration.

## Relationships

- **Parent:** `BaseBoard`
- **Children:** None
