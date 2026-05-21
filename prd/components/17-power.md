# Power Supply / Battery

> **CLI class:** `power`
> **WMI source:** `Win32_Battery` + `Win32_PortableBattery` + `Win32_UninterruptiblePowerSupply`
> **Hardware class:** `Power`
> **Tree position:** Child of `BaseBoard`
> **Generated:** 2026-05-21

## Overview

Represents power sources and batteries on the machine. It discovers and reports laptops batteries, portable batteries, and UPS units, listing capacity, chemistry, vendor, and serial information.

## Fields Collected

### From `Win32_Battery` / `Win32_PortableBattery` / `Win32_UninterruptiblePowerSupply`

| WMI Property | Hardware Field | Description |
|---|---|---|
| `DeviceID` | `id` | Device identifier, parsed as `"power:N"` where N is sequence |
| `Description` | `description` | Main device description (e.g. `"Primary Battery"`) |
| `Name` | `product` | Product/Model name of the power source |
| `Manufacturer` | `vendor` | Manufacturer of the battery / UPS |
| `SerialNumber` | `serial` | Serial number (if exposed by the hardware/driver) |
| `DesignCapacity` | `capacity` | Original design capacity in mWh |
| `Chemistry` | `configuration.chemistry` | Battery chemistry form factor (e.g. `"Lithium Ion"`) |

## Output Schema

```json
{
  "id": "power:0",
  "class": "power",
  "claimed": true,
  "handle": "",
  "description": "Primary Battery",
  "product": "Standard Battery",
  "vendor": "Dell OEM",
  "physid": "",
  "serial": "BAT-12345",
  "capacity": 56000,
  "configuration": {
    "chemistry": "Lithium Ion"
  }
}
```

## Interactions

### Full Scan (default invocation)

- **Trigger:** `lshw` — collected as child of `BaseBoard`
- **Behavior:** Queries batteries and UPS devices via WMI `SELECT *` query, populating corresponding `Power` nodes.

### Single Class Query

- **Trigger:** `lshw --class-hw power`
- **Behavior:** Queries power resources only.
- **On WMI failure:** Exits with error code `17`.

## Business Rules

- To handle missing attributes gracefully on custom Windows images or drivers (e.g., if `Chemistry` or `DesignCapacity` is not supported by the OS), WMI queries are performed using `SELECT *` and missing attributes are safely resolved via Python's exception handling layer, defaulting to an empty string.
- Design capacity is parsed into a clean integer value. If parsing fails, it defaults to `0`.

## Relationships

- **Parent:** `BaseBoard`
- **Children:** None
