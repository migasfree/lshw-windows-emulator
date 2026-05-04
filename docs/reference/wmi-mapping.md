# 🗺️ WMI Mapping Reference

The `lshw-windows-emulator` maps internal hardware classes to Windows Management Instrumentation (WMI).

## Mapping Table

| Hardware Class | WMI Method (Class) | Internal ID | Description |
| :--- | :--- | :--- | :--- |
| **system** | `Win32_ComputerSystem` | `core` | General system information (vendor, product, serial). |
| **baseboard** | `Win32_BaseBoard` | `motherboard` | Motherboard and manufacturer details. |
| **bios** | `Win32_bios` | `firmware` | BIOS version, date, and vendor. |
| **processor** | `Win32_Processor` | `cpu` | CPU model, speed, and cores. |
| **memory** | `Win32_PhysicalMemory` | `memory` | Physical RAM sticks. |
| **pci** | `Win32_Bus` | `pci` | PCI bridges and buses. |
| **ide** | `Win32_IDEController` | `ide` | Storage controllers. |
| **disk** | `Win32_DiskDrive` | `disk` | Physical disk information (HDDs, SSDs). |
| **partition** | `Win32_DiskPartition` | `partition` | Disk partitions. |
| **volume** | `Win32_LogicalDisk` | `volume` | Logical drives (C:, D:, etc.). |
| **usb** | `Win32_USBController` | `usb` | USB host controllers. |
| **usbdevices** | `Win32_USBControllerDevice` | `usbdevices` | Connected USB peripheral devices. |
| **cdrom** | `Win32_CDROMDrive` | `cdrom` | Optical drives and media. |
| **video** | `Win32_VideoController` | `display` | Graphics adapters and displays. |
| **network** | `Win32_NetworkAdapter` | `network` | Network interface cards (NICs). |
| **sound** | `Win32_SoundDevice` | `multimedia` | Audio and sound cards. |

## Property Extraction

Each class fetches specific WMI properties:

- **BIOS**: `Manufacturer`, `BIOSVersion`, `ReleaseDate`, `SerialNumber`.
- **Processor**: `Name`, `MaxClockSpeed`, `NumberOfCores`.
- **Disk Drive**: `Model`, `Size`, `InterfaceType`, `SerialNumber`.
- **Network Adapter**: `Name`, `MACAddress`, `AdapterType`.

## Custom Mapping

If you need to add a new hardware class or modify an existing mapping, refer to the [Adding Hardware Classes](../how-to/adding-hardware-classes.md) guide.

## Security

All WMI entity access is gated by `_WMI_ENTITY_ALLOWLIST` in `hardware_class.py`. Unknown entities are rejected with a logged `Security Alert`. The allowlist is case-insensitive — WMI entity names in this document use the canonical mixed case from the WMI provider, but validation compares against a normalized lowercase list. See [ADR 002: WMI Entity Allowlist](../adr/002-wmi-entity-allowlist.md) for details.
