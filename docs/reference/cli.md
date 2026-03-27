# 💻 Command Line Interface (CLI)

The `lshw-windows-emulator` (invoked as `lshw`) provides a command-line interface to query hardware information.

## Usage

```bash
lshw [options]
```

## Options

| Option | Shorthand | Description |
| :--- | :--- | :--- |
| `--help` | `-h` | Show the help message and exit. |
| `--json` | `-j` | Output hardware information in indented JSON format. |
| `--class-hw <class>` | `-c <class>` | Filter output to a specific hardware class. |

### Available Hardware Classes

You can use `-c list` to see the full list of supported classes:

- `system`: General computer system info.
- `baseboard`: Motherboard details.
- `bios`: Firmware and BIOS version.
- `processor`: CPU details.
- `memory`: Physical RAM modules.
- `pci`: PCI bus and bridge information.
- `ide`: IDE controllers.
- `disk`: Physical disk drives.
- `partition`: Disk partitions.
- `volume`: Logical drives and volumes.
- `usb`: USB controllers.
- `usbdevices`: Connected USB devices.
- `cdrom`: Optical drives.
- `video`: Graphics cards.
- `network`: Network adapters.
- `sound`: Multimedia and sound devices.

## Output Formats

### Standard Text

By default, `lshw` prints a tree-like structure (indented text) showing hardware properties and their values.

### JSON

Using the `--json` flag, the tool returns a JSON array of objects. This is highly recommended for integration with other tools (like `migasfree-client`).

## Exit Codes

The tool uses specific exit codes to indicate different types of failures:

| Code | Meaning |
| :--- | :--- |
| `0` | Success. |
| `1` | Usage error or invalid class. |
| `2-15` | Hardware specific error (e.g., error getting BIOS info). |
| `16` | Critical error getting system-wide hardware information. |
