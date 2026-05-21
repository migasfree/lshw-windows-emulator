# CD/DVD-ROM Drive

> **CLI class:** `cdrom`
> **WMI source:** `Win32_CDROMDrive`
> **Hardware class:** `CdRom`
> **Tree position:** Child of `Ide` — leaf node (no children)
> **Generated:** 2026-05-20

## Overview

Represents an optical drive (CD-ROM, DVD-ROM, Blu-ray). When attached as a child of an IDE controller, only the drive associated with a specific PNP ID is fetched. When queried standalone, all optical drives on the system are returned.

## Fields Collected

| WMI Property | Hardware Field | Description |
|---|---|---|
| `Description` | `description` | Drive description (e.g. `"CD-ROM Drive"`) |
| `Name` | `product` | Drive model name |
| `Manufacturer` | `vendor` | Drive manufacturer |
| `Drive` | `logicalname` | Drive letter (e.g. `"D:"`) |
| `DeviceID` | `deviceid` | WMI device identifier |
| `PNPDeviceID` | `pnpdeviceid` | PnP identifier |
| `MediaLoaded` | `configuration.status` | Boolean → `"loaded disc"` / `"no disc"` |

Collected but not mapped: `Caption`, `MediaType`, `SCSIBus`, `SCSILogicalUnit`, `SCSIPort`.

## Fixed Fields

| Field | Value |
|-------|-------|
| `id` | `"cdrom"` |
| `class` | `"disk"` |
| `claimed` | `true` |
| `businfo` | `""` |
| `dev` | `""` |
| `version` | `""` |
| `capabilities` | `{removable:"", audio:"", cd-r:"", cd-rw:"", dvd:"", dvd-r:"", dvd-ram:""}` |

## Output Schema

```json
{
  "id": "cdrom",
  "class": "disk",
  "claimed": true,
  "description": "CD-ROM Drive",
  "product": "HL-DT-ST DVDRAM GUE1N",
  "vendor": "HL-DT-ST",
  "logicalname": "D:",
  "deviceid": "IDE\\CDROMHL-DT-ST_DVDRAM_GUE1N...",
  "pnpdeviceid": "IDE\\CDROMHL-DT-ST_DVDRAM_GUE1N...",
  "configuration": {
    "ansiversion": "",
    "status": "no disc"
  },
  "capabilities": {
    "removable": "",
    "audio": "",
    "cd-r": "",
    "cd-rw": "",
    "dvd": "",
    "dvd-r": "",
    "dvd-ram": ""
  }
}
```

## Interactions

### As Child of IDE (Full Scan)

- **Trigger:** `lshw` via `Ide._attach_ide_child()`
- **Instantiation:** `CdRom(pnp_device_id)` — queries `Win32_CDROMDrive WHERE PNPDeviceID LIKE "%{dev_id}%"`.

### As Standalone Query

- **Trigger:** `lshw --class-hw cdrom`
- **Instantiation:** `CdRom()` (no dev_id) — queries all `Win32_CDROMDrive` records.
- **On WMI failure:** Exits with error code `12`.

## Business Rules

- All capability fields (`removable`, `audio`, `cd-r`, `cd-rw`, `dvd`, `dvd-r`, `dvd-ram`) are always empty strings. They are structural placeholders consistent with Linux `lshw` format but not populated from WMI data.
- `configuration.ansiversion` is always `""`.
- `MediaLoaded` conversion: `True` → `"loaded disc"`, any other value (including `None` or `False`) → `"no disc"`.
- `Caption`, `MediaType`, `SCSIBus`, `SCSILogicalUnit`, and `SCSIPort` are included in `properties_to_get` but none are mapped to `Hardware` fields.

## Relationships

- **Parent:** `Ide`
- **No children.**
