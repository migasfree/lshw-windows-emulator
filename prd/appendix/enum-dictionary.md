# Enum Dictionary

All enumerations, status codes, type mappings, and constants used throughout the LsHw Windows Emulator codebase.

---

## ChassisTypes

Source: `computer_system.py` → `get_chassis()` → `Win32_SystemEnclosure.ChassisTypes[0]`

The WMI chassis type code is a 1-based integer index. The tool maps it to a human-readable string:

| Code | String Value |
|------|-------------|
| 1 | `"Maybe Virtual Machine"` |
| 2 | `"??"` |
| 3 | `"Desktop"` |
| 4 | `"low-profile"` |
| 5 | `"Pizza Box"` |
| 6 | `"mini-tower"` |
| 7 | `"Full Tower"` |
| 8 | `"Portable"` |
| 9 | `"Laptop"` |
| 10 | `"notebook"` |
| 11 | `"Hand Held"` |
| 12 | `"Docking Station"` |
| 13 | `"All in One"` |
| 14 | `"Sub Notebook"` |
| 15 | `"Space-Saving"` |
| 16 | `"Lunch Box"` |
| 17 | `"Main System Chassis"` |
| 18 | `"Lunch Box"` *(duplicate of 16 — as-is in source)* |
| 19 | `"SubChassis"` |
| 20 | `"Bus Expansion Chassis"` |
| 21 | `"Peripheral Chassis"` |
| 22 | `"Storage Chassis"` |
| 23 | `"Rack Mount Unit"` |
| 24 | `"Sealed-Case PC"` |
| *out of range* | `"Unknown"` (fallback) |

---

## MemoryType

Source: `Win32_PhysicalMemory.MemoryType` (integer, stored in `product` field)

| Code | Memory Type |
|------|------------|
| 0 | Unknown |
| 1 | Other |
| 2 | DRAM |
| 3 | Synchronous DRAM |
| 4 | Cache DRAM |
| 5 | EDO |
| 6 | EDRAM |
| 7 | VRAM |
| 8 | SRAM |
| 9 | RAM |
| 10 | ROM |
| 11 | Flash |
| 12 | EEPROM |
| 13 | FEPROM |
| 14 | EPROM |
| 15 | CDRAM |
| 16 | 3DRAM |
| 17 | SDRAM |
| 18 | SGRAM |
| 19 | RDRAM |
| 20 | DDR |
| 21 | DDR2 |
| 22 | DDR2 FB-DIMM |
| 24 | DDR3 |
| 26 | DDR4 |

> **Note:** The raw integer is stored in the `product` field without string conversion. Consumers must perform their own mapping.

---

## USB Device ClassGuid

Source: `usb_device.py` → `_populate_hardware()` → `ClassGuid`

Language-neutral GUID-based device classification:

| ClassGuid | Assigned `id` | Human Description |
|-----------|--------------|-------------------|
| `{4d36e96b-e325-11ce-bfc1-08002be10318}` | `usb_teclado` | Keyboard |
| `{4d36e96f-e325-11ce-bfc1-08002be10318}` | `usb_mouse` | Mouse / Pointer Device |
| `{4d36e967-e325-11ce-bfc1-08002be10318}` | `usb_disk` | Disk (storage) |
| `{71a27cdd-817f-11d0-bec7-08002be2092f}` | `usb_vol` | Volume |
| `{745a17a0-74d3-11d0-b6fe-00a0c90f57da}` | *(excluded)* | Generic HID — filtered out |
| *(any other)* | `usb_device` | Generic USB device |

---

## USB Device Excluded Services

Source: `usb_device.py` → `get_hardware()` → `excluded_services`

Devices with these `Service` values are silently excluded from the output:

| Service | Excluded Category |
|---------|------------------|
| `usbccgp` | USB Composite Device (driver aggregator) |
| `USBSTOR` | USB Mass Storage (raw block device) |
| `usbhub` | USB Root Hub |

---

## PCI Bus ID Prefixes

Source: `pci.py` → `_populate_hardware()` → `DeviceID` prefix detection

| WMI `DeviceID` Prefix | Assigned ID Format | Example |
|-----------------------|-------------------|---------|
| `ISA\` | `isa:{last_char}` | `isa:0` |
| `PCI\` | `pci:{last_char}` | `pci:0` |
| `PnpBus\` (first 3: `pnp`) | `pnp:{last_char}` | `pnp:0` |
| *(any other prefix)* | `""` (empty) | |

---

## Exit Codes

Source: `__main__.py` → `_exit_manager()` + `EXIT_USAGE`

| Exit Code | Meaning | Hardware Class |
|-----------|---------|---------------|
| `0` | Success | — |
| `1` | Error getting ComputerSystem | `system` |
| `2` | Error getting BaseBoard or Firmware | `baseboard`, `bios` |
| `3` | Error getting Processor | `processor` |
| `4` | Error getting PhysicalMemory | `memory` |
| `5` | Error getting Pci | `pci` |
| `6` | Error getting Ide | `ide` |
| `7` | Error getting PhysicalDisk | `disk` |
| `8` | Error getting PartitionDisk | `partition` |
| `9` | Error getting LogicalDisk | `volume` |
| `10` | Error getting Usb | `usb` |
| `11` | Error getting UsbDevice | `usbdevices` |
| `12` | Error getting CdRom | `cdrom` |
| `13` | Error getting GraphicCard | `video` |
| `14` | Error getting NetworkCard | `network` |
| `15` | Error getting SoundDevice | `sound` |
| `16` | Critical error (full scan) | Full system |
| `EXIT_USAGE = 1` | Unknown `--class-hw` argument | — |

---

## WMI Entity Allowlist

Source: `hardware_class.py` → `HardwareClass._WMI_ENTITY_ALLOWLIST`

The complete set of 22 permitted WMI entity names (stored normalized to lowercase):

```
win32_baseboard
win32_bios
win32_bus
win32_cdromdrive
win32_computersystem
win32_computersystemproduct
win32_diskdrive
win32_diskdrivetodiskpartition
win32_diskpartition
win32_idecontroller
win32_idecontrollerdevice
win32_logicaldisk
win32_logicaldisktopartition
win32_networkadapter
win32_physicalmemory
win32_pnpentity
win32_processor
win32_sounddevice
win32_systemenclosure
win32_usbcontroller
win32_usbcontrollerdevice
win32_videocontroller
```

Any WMI access attempt against an entity not in this list is rejected with a `ValueError` and logged as a security alert.

---

## Logical Disk Drive Letter Index

Source: `logical_disk.py` → `_populate_hardware()` → `drive_letters`

The `id` field for logical volumes is computed as `"logicalvolume:{index}"` where index is the position of the drive letter in the string `"ABCDEFGHIJKLMNOPQRSTUVWXYZ"`:

| Drive Letter | Index | `id` |
|-------------|-------|------|
| A: | 0 | `logicalvolume:0` |
| B: | 1 | `logicalvolume:1` |
| C: | 2 | `logicalvolume:2` |
| D: | 3 | `logicalvolume:3` |
| … | … | … |
| Z: | 25 | `logicalvolume:25` |

If the first character of `DeviceID` is not an ASCII uppercase letter, id defaults to `"Error getting data"`.
