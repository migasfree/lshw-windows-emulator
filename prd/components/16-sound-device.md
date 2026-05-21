# Sound Device

> **CLI class:** `sound`
> **WMI source:** `Win32_SoundDevice`
> **Hardware class:** `SoundDevice`
> **Tree position:** Child of `Pci` — leaf node (no children)
> **Generated:** 2026-05-20

## Overview

Represents audio devices (sound cards, HD Audio controllers). One record is returned per audio device detected. Reports the manufacturer as the product name and captures PNP identifiers.

## Fields Collected

| WMI Property | Hardware Field | Description |
|---|---|---|
| `Manufacturer` | `product` | Audio device manufacturer / product name |
| `PNPDeviceID` | `pnpdeviceid` | PnP identifier |
| `DeviceID` | `deviceid` | WMI device identifier |

## Fixed Fields

| Field | Value |
|-------|-------|
| `id` | `"multimedia"` |
| `class` | `"multimedia"` |
| `claimed` | `true` |
| `description` | `"Audio device"` |
| `businfo` | `""` |
| `version` | `""` |
| `width` | `0` |
| `clock` | `0` |
| `serial` | `""` |
| `configuration` | `{driver: "", latency: ""}` |
| `capabilities` | `{pm:"", msi:"", pciexpress:"", bus_master:"", cap_list:""}` |

## Output Schema

```json
{
  "id": "multimedia",
  "class": "multimedia",
  "claimed": true,
  "description": "Audio device",
  "product": "Realtek Semiconductor Corp.",
  "pnpdeviceid": "HDAUDIO\\FUNC_01&VEN_10EC&...",
  "deviceid": "ROOT\\MEDIA\\0000",
  "configuration": {
    "driver": "",
    "latency": ""
  },
  "capabilities": {
    "pm": "",
    "msi": "",
    "pciexpress": "",
    "bus_master": "",
    "cap_list": ""
  }
}
```

## Interactions

### Full Scan / Single Class Query

- **Trigger:** `lshw` or `lshw --class-hw sound`
- **Behavior:** Queries `Win32_SoundDevice` for all audio devices.
- **On WMI failure:** Exits with error code `15`.

## Business Rules

- `product` is populated from `Manufacturer`, not from a dedicated product/model field. This may cause the product to display manufacturer name only (e.g. `"Realtek Semiconductor Corp."`).
- `vendor` is never populated — no WMI property is mapped to it (defaults to `"Error getting data"`).
- All capability and configuration keys are empty placeholder strings.

## Relationships

- **Parent:** `Pci`
- **No children.**
