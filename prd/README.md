# LsHw Windows Emulator — Product Requirements Document

> **Version:** 1.0.0
> **Generated:** 2026-05-20
> **Method:** Reverse-engineered from source code using the `code-to-prd` skill (v2.1.2)
> **Authors:** Jose Antonio Chavarría, Alfonso Gómez Sánchez
> **License:** GPL-3.0-or-later

---

## System Overview

**LsHw Windows Emulator** (`lshw`) is a command-line tool that brings the hardware introspection capabilities of the Linux `lshw` utility to the Windows platform. It uses Windows Management Instrumentation (WMI) to gather structured hardware inventory data — identical in output format to the original Linux tool — making it a drop-in complement for cross-platform fleet management systems such as **Migasfree**.

The tool queries 16 distinct hardware classes via WMI and assembles the results into a hierarchical device tree that mirrors the physical architecture of the machine: from the top-level computer system, down through the motherboard, to every individual disk partition and USB peripheral. The output can be rendered either as human-readable key-value pairs or as JSON, enabling both operator inspection and programmatic consumption by management agents.

Primary users are **system administrators** and **software management agents** (particularly `migasfree-client`) that need a reliable, scriptable hardware inventory on Windows endpoints. The tool requires no interactive UI — it is invoked from the command line or called programmatically as a Python library.

---

## Module Overview

| Module | Components | Core Functionality |
|--------|-----------|-------------------|
| **CLI Entry Point** | `__main__` | Argument parsing, dispatch, output formatting |
| **System Layer** | `ComputerSystem`, `BaseBoard`, `Firmware` | Machine identity, motherboard, BIOS |
| **Compute Layer** | `Processor`, `PhysicalMemory`, `CacheMemory` | CPU, RAM, and L1/L2/L3 cache inventory |
| **Storage Layer** | `Ide`, `PhysicalDisk`, `PartitionDisk`, `LogicalDisk`, `CdRom` | Full disk hierarchy |
| **Expansion Bus** | `Pci`, `GraphicCard`, `SoundDevice`, `NetworkCard`, `Communication` | PCI devices, serial ports, modems, and network/audio peripherals |
| **USB Subsystem** | `Usb`, `UsbDevice` | USB controllers and connected devices |
| **Power & Print** | `Power`, `Printer` | Batteries, UPS, printer queues and drivers |
| **Core Framework** | `HardwareClass`, `Hardware`, `WMIConnection` | Base patterns, data model, WMI singleton |

---

## Component Inventory

| # | Component | CLI Class | WMI Source | Doc Link |
|---|-----------|-----------|-----------|----------|
| 1 | Computer System | `system` | `Win32_ComputerSystem` | [→](./components/01-computer-system.md) |
| 2 | Base Board (Motherboard) | `baseboard` | `Win32_BaseBoard` | [→](./components/02-base-board.md) |
| 3 | Firmware (BIOS) | `bios` | `Win32_Bios` | [→](./components/03-firmware.md) |
| 4 | Processor (CPU) | `processor` | `Win32_Processor` | [→](./components/04-processor.md) |
| 5 | Physical Memory (RAM) | `memory` | `Win32_PhysicalMemory` | [→](./components/05-physical-memory.md) |
| 6 | PCI Bus | `pci` | `Win32_Bus` | [→](./components/06-pci.md) |
| 7 | IDE Controller | `ide` | `Win32_IDEController` | [→](./components/07-ide.md) |
| 8 | Physical Disk | `disk` | `Win32_DiskDrive` | [→](./components/08-physical-disk.md) |
| 9 | Disk Partition | `partition` | `Win32_DiskPartition` | [→](./components/09-partition-disk.md) |
| 10 | Logical Volume | `volume` | `Win32_LogicalDisk` | [→](./components/10-logical-disk.md) |
| 11 | USB Controller | `usb` | `Win32_USBController` | [→](./components/11-usb.md) |
| 12 | USB Device | `usbdevices` | `Win32_USBControllerDevice` | [→](./components/12-usb-device.md) |
| 13 | CD/DVD-ROM Drive | `cdrom` | `Win32_CDROMDrive` | [→](./components/13-cd-rom.md) |
| 14 | Graphics Card | `video` | `Win32_VideoController` | [→](./components/14-graphic-card.md) |
| 15 | Network Card (NIC) | `network` | `Win32_NetworkAdapter` | [→](./components/15-network-card.md) |
| 16 | Sound Device | `sound` | `Win32_SoundDevice` | [→](./components/16-sound-device.md) |
| 17 | Power Source | `power` | `Win32_Battery`, `Win32_PortableBattery`, `Win32_UninterruptiblePowerSupply` | [→](./components/17-power.md) |
| 18 | Printer | `printer` | `Win32_Printer` | [→](./components/18-printer.md) |
| 19 | Communication | `communication` | `Win32_SerialPort`, `Win32_POTSModem` | [→](./components/19-communication.md) |
| 20 | Cache Memory | `memory` | `Win32_CacheMemory` | [→](./components/20-cache-memory.md) |

---

## CLI Interface

```cmd
lshw [--json | -j | -json] [--class-hw CLASS | -c CLASS]
```

| Argument | Alias | Behavior |
|----------|-------|----------|
| *(none)* | | Full scan: returns the complete hardware tree from `ComputerSystem` down |
| `--json` | `-j`, `-json` | Renders output as indented JSON array instead of key-value text |
| `--class-hw CLASS` | `-c CLASS` | Queries a single hardware class only (no children) |
| `--class-hw list` | `-c list` | Prints the list of valid class names and exits |

---

## Appendix

| Document | Contents |
|----------|----------|
| [Enum Dictionary](./appendix/enum-dictionary.md) | All enumerations: chassis types, memory types, USB ClassGuids, PCI bus prefixes, exit codes, WMI allowlist, drive letter index |
| [Component Relationships](./appendix/component-relationships.md) | Device tree diagram, parent→child registry, CLI class mapping, cross-class data coupling, singleton/shared state |
| [Data Model](./appendix/data-model.md) | `Hardware` dataclass field reference, serialization rules, dynamic attributes, error sentinels |
| [Security Model](./appendix/security-model.md) | Threat model, WMI allowlist, WQL sanitization, permission requirements, sensitive data in output |
| [WMI Query Reference](./appendix/wmi-query-reference.md) | Every WMI query executed per hardware class, with query pattern, fields, and conditions |
| [Linux Parity Specification](./appendix/parity-specification.md) | Full technical specification and multi-phase implementation roadmap to achieve 100% feature parity with Linux `lshw` |

---

## Global Notes

### Device Tree Architecture

The hardware inventory is a **depth-first tree** rooted at `ComputerSystem`. When invoked without `--class-hw`, the tool walks the full tree recursively:

```txt
ComputerSystem
└── BaseBoard
    ├── Firmware (BIOS)
    ├── Processor (one entry per physical socket)
    │   └── CacheMemory (L1/L2/L3 nested cache segments)
    ├── PhysicalMemory (container → bank children)
    ├── Power (power supplies & battery modules)
    ├── Printer (printer queues and drivers)
    └── Pci
        ├── Ide
        │   ├── PhysicalDisk
        │   │   └── PartitionDisk
        │   │       └── LogicalDisk
        │   └── CdRom
        ├── GraphicCard
        ├── SoundDevice
        ├── NetworkCard
        ├── Communication (serial ports & modems)
        └── Usb (one entry per USB controller)
            └── UsbDevice (filtered, one per attached device)
```

### Data Model

Every hardware node is a `Hardware` dataclass with 30 fields. Fields with no value are omitted from JSON output. The `children` field carries sub-components as a nested list.

### Error Handling

When a WMI query fails for a class, the tool:

- Returns `"Error getting data"` (`__ERROR__`) as field placeholders
- Logs the error at `WARNING` or `ERROR` level
- Continues collecting other classes (does not abort the full scan)
- Exits with error code 1–16 only when `--class-hw` is specified for the failing class; code 16 for a full-scan failure

### Security Model

All WMI entity names must appear in `_WMI_ENTITY_ALLOWLIST` (22 normalized lowercase entries). Queries against unlisted entities are rejected with a logged security alert and a `ValueError`. WQL string values are sanitized by stripping `"`, `'`, and `;` characters before interpolation.

### Permission Requirements

WMI queries require the calling process to have **local administrator privileges** on the Windows machine. Without elevation, queries may return `wmi.x_access_denied` exceptions, which are caught and reported via the exit manager.

### Output Formats

| Format | Trigger | Description |
|--------|---------|-------------|
| Human-readable | *(default)* | Indented `key: value` pairs via `pretty()` |
| JSON | `--json` | `json.dumps(list_of_dicts, indent=2)` |

### Platform Compatibility

- **Runtime**: Windows 10+ (WMI required)
- **Cross-platform development**: On non-Windows systems the `wmi` module is replaced by a stub, allowing unit tests to run on Linux/macOS via mock injection in `tests/conftest.py`
- **Python**: 3.6+ (with `dataclasses` backport for Python < 3.7)
