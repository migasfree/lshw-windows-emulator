# First Hardware Inventory with lshw

This tutorial walks you through your first hardware inventory scan on a Windows machine using `lshw-windows-emulator`. You will install the tool, run a full system scan, and export the results as JSON.

By the end, you will have a complete hardware report of your Windows computer, compatible with the `lshw` format used on Linux systems.

## Prerequisites

- **Windows 10 or later** (64-bit)
- **Python 3.8 or later** installed. If you don't have Python, download it from [python.org](https://python.org).
- **Administrator privileges** on the machine you are scanning

## Step 1: Install lshw-windows-emulator

Open **Command Prompt** as Administrator, then create a virtual environment and install the tool:

```cmd
:: Create a directory for the tool
mkdir C:\tools\lshw
cd C:\tools\lshw

:: Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate

:: Install lshw-windows-emulator
pip install lshw
```

When the installation finishes, verify it worked:

```cmd
lshw --help
```

You should see the help text listing all available options and hardware classes.

## Step 2: Run Your First Scan

Run a full system scan with default (text) output:

```cmd
lshw
```

You will see a tree of hardware components printed to the terminal, starting with `ComputerSystem` and descending through `BaseBoard`, `Processor`, `PhysicalMemory`, storage controllers, disk drives, network cards, and more.

Example output fragment:

```
        product: Precision 5560
        vendor: Dell Inc.
        serial: ABC123
    BaseBoard:
        product: 0F3Y8T
        vendor: Dell Inc.
    Processor:
        product: 11th Gen Intel(R) Core(TM) i7-11850H @ 2.50GHz
        clock: 2496
```

## Step 3: Export Results as JSON

The text output is useful for quick inspection, but JSON is better for integration with other tools (such as `migasfree-client`):

```cmd
lshw --json > inventory.json
```

Open `inventory.json` in any text editor. The structure is an array of hardware objects, each with fields like `id`, `class`, `vendor`, `product`, `serial`, and `children` for nested components.

Example JSON entry:

```json
[
  {
    "id": "computer:0",
    "class": "system",
    "claimed": true,
    "description": "Computer System",
    "product": "Precision 5560",
    "vendor": "Dell Inc.",
    "serial": "ABC123",
    "children": []
  }
]
```

## Step 4: Scan a Single Hardware Class

If you need information about a specific component instead of the full system, use the `--class-hw` (short: `-c`) option:

```cmd
:: Get only memory information
lshw --class-hw memory

:: Get only network adapter information
lshw -c network

:: List all available classes
lshw -c list
```

Combine with `--json` for single-class JSON output:

```cmd
lshw -c memory --json
```

## Step 5: Understanding the Output

Each hardware component in the output includes:

| Field | Meaning | Example |
|---|---|---|
| `id` | Unique identifier within the hardware tree | `processor:0` |
| `class` | Hardware category (system, processor, memory, disk, network, etc.) | `memory` |
| `claimed` | Whether the OS has a driver claiming this device | `true` |
| `product` | Product name or model | `11th Gen Intel(R)...` |
| `vendor` | Manufacturer name | `Dell Inc.` |
| `serial` | Serial number (may be empty on some hardware) | `ABC123` |
| `children` | Nested sub-components (e.g., partitions inside a disk) | `[...]` |

## Troubleshooting

**"lshw is not recognized"**: Make sure the virtual environment is activated (you should see `(.venv)` in your prompt).

**Access denied errors**: Run Command Prompt as Administrator. WMI queries require elevated privileges.

**Empty or missing fields**: Some hardware (especially virtual machines) may not expose full WMI data. This is expected — the tool reports what WMI provides.

**JSON output is empty**: Try running without `--json` first to see any error messages.

## Next Steps

- Read the [CLI Reference](../reference/cli.md) for all available options
- Learn how to [integrate the Python API](../how-to/using-the-python-api.md) into your scripts
- Add a [new hardware class](../how-to/adding-hardware-classes.md) if your device is not yet supported
- Review the [Architecture](../explanation/architecture.md) to understand how the tool works internally
