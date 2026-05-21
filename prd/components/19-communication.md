# Communication Device

> **CLI class:** `communication`
> **WMI source:** `Win32_SerialPort` + `Win32_POTSModem`
> **Hardware class:** `Communication`
> **Tree position:** Child of `Pci` (under expansion slot bridge)
> **Generated:** 2026-05-21

## Overview

Discovers and inventories communication channels, primarily standard COM Serial Ports and active modems. Reports maximum transfer rates and active COM ports.

## Fields Collected

### From `Win32_SerialPort` / `Win32_POTSModem`

| WMI Property | Hardware Field | Description |
|---|---|---|
| `DeviceID` | `id` | Communication channel, sequence parsed as `"communication:N"` |
| `Description` / `Caption` | `description` | Device description (e.g. `"Communications Port"`) |
| `Name` | `product` | Name of the serial port or modem model |
| `Manufacturer` / `ProviderName` / `ProviderType` | `vendor` | Port vendor / provider name |
| `DeviceID` / `AttachedTo` | `logicalname` | Associated port name (e.g., `"COM1"`, `"COM2"`) |
| `MaxBaudRate` | `clock` | Speed in baud |

## Output Schema

```json
{
  "id": "communication:0",
  "class": "communication",
  "claimed": true,
  "handle": "",
  "description": "Communications Port",
  "product": "Communications Port (COM1)",
  "vendor": "Standard Port",
  "logicalname": "COM1",
  "clock": 115200
}
```

## Interactions

### Full Scan (default invocation)

- **Trigger:** `lshw` — collected under the Expansion Bus bridge (`Pci`)
- **Behavior:** Discovers serial interfaces and POTS modems using `SELECT *` query and maps them into the device tree.

### Single Class Query

- **Trigger:** `lshw --class-hw communication`
- **Behavior:** Queries communications devices only.
- **On WMI failure:** Exits with error code `19`.

## Business Rules

- Maximum speeds are parsed and assigned to the `clock` field in baud to represent physical frequency parities.
- Vendor extraction runs through a safe chain (checking `Manufacturer` → `ProviderName` → `ProviderType`) to find the most accurate supplier.
- Standard WQL validation allowlist guards against WQL injections.

## Relationships

- **Parent:** `Pci`
- **Children:** None
