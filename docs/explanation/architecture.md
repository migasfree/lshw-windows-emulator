# 🏗️ LsHw Windows Emulator Architecture

This document provides a deep dive into the `lshw-windows-emulator` architecture, explaining the design decisions behind its implementation as a WMI-based hardware emulator for Windows.

## 📐 High-Level Overview

The core of the application is the `HardwareClass`, an abstract base class that implements the **Factory Pattern**. Specific hardware components inherit from this class and implement their own data retrieval and formatting logic.

### 🧩 Core Components

| Component | Role |
| :--- | :--- |
| **HardwareClass** | Abstract Base Class (ABC) that handles the WMI connection (via `WMIConnection` singleton) and provides utility methods for WQL queries (`build_wql_select`, `execute_wql_query`). |
| **Factory Pattern** | The `HardwareClass` uses a registration decorator/factory method to instantiate the correct class based on the hardware entity string (e.g., 'processor', 'network'). |
| **WMI Connection** | Managed by a Singleton class `WMIConnection` to ensure efficient resource usage throughout the application lifecycle. |

## ⛓️ Hardware Tree & Hierarchy

The emulator produces a hierarchical representation of hardware, modeled after the original `lshw` structure.

```mermaid
graph TD
    %% 1. Node Declarations
    CS["ComputerSystem"]
    BB["BaseBoard"]
    FW["Firmware"]
    PR["Processor"]
    PM["PhysicalMemory"]
    PCI["Pci"]
    IDE["Ide"]
    PD["PhysicalDisk"]
    PAR["PartitionDisk"]
    LD["LogicalDisk"]
    USB["Usb"]
    UD["UsbDevice"]
    CD["CdRom"]
    GC["GraphicCard"]
    SD["SoundDevice"]
    NIC["NetworkCard"]

    %% 2. Connection Logic (Parent → Child)
    CS --> BB
    BB --> FW
    BB --> PR
    BB --> PM
    BB --> PCI
    PCI --> IDE
    PCI --> USB
    PCI --> GC
    PCI --> SD
    PCI --> NIC
    IDE --> PD
    IDE --> CD
    PD --> PAR
    PAR --> LD
    USB --> UD
```

## 🔄 Data Fetching Lifecycle

When a hardware inquiry is made (e.g., `lshw --json`), the following flow is executed:

1. **CLI Entry Point** (`__main__.py`): Parses arguments and requests a specific hardware class (or 'ComputerSystem' for full system discovery).
2. **Factory Resolving**: The `HardwareClass.factory()` method instantiates the requested class based on its registered string name.
3. **WMI Connection**: The instance retrieves the `WMIConnection` singleton.
4. **Retrieval Phase**: `get_hardware()` executes WQL queries to pull raw data from Windows Management Instrumentation.
5. **Standardization**: The `format_data()` method maps raw WMI attributes to a consistent dictionary structure, handling missing values and data normalization.
6. **Child Discovery**: If requested, the class recursively calls `format_data(children=True)` on its registered children classes.
7. **Serialization**: The final tree is serialized to the requested output format (JSON or Pretty Text).

## 🛡️ Design Decisions & Constraints

- **Python 3.6 Support**: Maintaining compatibility with Python 3.6 is a hard-stop requirement for legacy integration.
- **WMI Reliability**: The architecture abstracts WMI queries to handle platform-specific deviations and performance bottlenecks gracefully.
- **No Native Dependencies**: The project relies exclusively on standard WMI calls (via the `wmi` package) and `psutil` to avoid complex native compilation requirements on Windows.

---
> [!NOTE]
> This document follows the **Diátaxis Explanation Quadrant**, focusing on why the system is built this way rather than how to use it.
