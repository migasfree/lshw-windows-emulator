# USB Device

> **CLI class:** `usbdevices`
> **WMI sources:** `Win32_USBControllerDevice`, `Win32_PNPEntity`
> **Hardware class:** `UsbDevice`
> **Tree position:** Child of `Usb` — leaf node (no children)
> **Generated:** 2026-05-20

## Overview

Represents individual USB peripheral devices attached to a USB host controller. The class filters out composite devices, mass storage drivers, root hubs, and generic HID devices to present only meaningful user-visible peripherals. Each device is classified by its `ClassGuid` into a descriptive category identifier.

## Fields Collected

| WMI Property | Hardware Field | Description |
|---|---|---|
| `Caption` | *(used for SmartBoard detection)* | Display name |
| `Description` | `class_`, `description`, `vendor` | Device class description |
| `DeviceID` | `deviceid` | WMI device path |
| `PNPDeviceID` | `pnpdeviceid` | PnP identifier |
| `ClassGuid` | `id` (via classification) | Used to determine device category |
| `Service` | `service` | Driver service name |
| `Parent_PNPDeviceID` | `parent_pnpdeviceid` | Controller PNP ID (injected from association) |

> **Note:** `class_guid` and `service` are set as attributes on the `Hardware` object dynamically; they are not part of the base `Hardware` dataclass. This means they will **not** appear in `to_dict()` output.

## Device Classification (ClassGuid → ID)

| ClassGuid | Assigned `id` | Device Type |
|-----------|--------------|-------------|
| `{4d36e96b-e325-11ce-bfc1-08002be10318}` | `usb_teclado` | Keyboard |
| `{4d36e96f-e325-11ce-bfc1-08002be10318}` | `usb_mouse` | Mouse / pointing device |
| `{4d36e967-e325-11ce-bfc1-08002be10318}` | `usb_disk` | Disk storage device |
| `{71a27cdd-817f-11d0-bec7-08002be2092f}` | `usb_vol` | Volume / storage volume |
| Caption contains `"SmartBoard"` | `usb_smartboard_xx44` | Interactive whiteboard |
| *(any other ClassGuid)* | `usb_device` | Generic USB device |

## Excluded Devices (Filtered Out)

| Filter Type | Value | Excluded Category |
|------------|-------|------------------|
| `Service` | `usbccgp` | USB Composite Device |
| `Service` | `USBSTOR` | USB Mass Storage (raw) |
| `Service` | `usbhub` | USB Root Hub |
| `ClassGuid` | `{745a17a0-74d3-11d0-b6fe-00a0c90f57da}` | Generic HID |

## Output Schema

```json
{
  "id": "usb_mouse",
  "class": "USB Input Device",
  "claimed": true,
  "description": "USB Input Device",
  "vendor": "USB Input Device",
  "pnpdeviceid": "USB\\VID_046D&PID_C52B&...",
  "parent_pnpdeviceid": "PCI\\VEN_8086&DEV_A36D&..."
}
```

## Interactions

### As Child of Usb Controller (Full Scan)

- **Trigger:** `lshw` via `Usb._fetch_children()`
- **Instantiation:** `UsbDevice(dev_id=[controller_pnpdeviceid])` — device list is pre-filtered to only this controller's children.
- **Association walk:** Queries all `Win32_USBControllerDevice` associations. For each association whose `Antecedent` matches the controller PNP ID, queries the corresponding `Win32_PNPEntity` by `PNPDeviceID`.

### As Standalone Query

- **Trigger:** `lshw --class-hw usbdevices`
- **Instantiation:** `UsbDevice()` (no dev_id) — queries all USB controllers and all their associated devices.
- **On WMI failure:** Exits with error code `11`.

## Business Rules

- `class_` (the lshw `class` field) is set to the WMI `Description` string, not a standard hardware class name. This differs from all other hardware classes.
- `description` and `vendor` are also set to `Description` — all three fields receive the same value.
- `class_guid` and `service` are set dynamically on the object; they are Python attributes outside the dataclass definition. They do **not** appear in the JSON output from `to_dict()`.
- Deduplication: `Win32_USBControllerDevice` can produce duplicate entries; deduplication of the controller set is done via `set()` on the antecedent values before the device enumeration loop.

## Relationships

- **Parent:** `Usb`
- **No children.**
