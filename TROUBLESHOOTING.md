# Admin Troubleshooting Guide for lshw-windows-emulator

This guide addresses common issues administrators may encounter when gathering hardware inventory on Windows using `lshw-windows-emulator`.

## 1. WMI Access Denied Errors

**Symptoms:**

- Error messages containing `x_access_denied`.
- Partial inventory data.
- "Access denied" logs in the console.

**Causes:**

- The user running the script does not have Administrator privileges.
- WMI permissions are restricted for the user account.
- UAC (User Account Control) is blocking WMI queries.

**Solutions:**

- **Run as Administrator**: Ensure the command prompt or PowerShell session is launched with "Run as Administrator".
- **Check WMI Permissions**:
  1. Run `wmimgmt.msc`.
  2. Right-click "WMI Control (Local)" -> Properties.
  3. Go to "Security" tab.
  4. Ensure the user has "Enable Account" and "Remote Enable" permissions for `Root\CIMv2`.

## 2. Missing Hardware Data

**Symptoms:**

- JSON output contains empty fields (e.g., `"serial": ""`, `"product": "Unknown"`).
- Certain hardware classes (e.g., `tape_drives`) are missing entirely.

**Causes:**

- Minimum WMI implementation on some Windows versions (e.g., Windows Home).
- Missing drivers for specific hardware components.
- Virtual Machine environments masking physical hardware details.

**Solutions:**

- **Update Drivers**: Ensure all chipset and manufacturer drivers are installed. Generic Microsoft drivers may not expose full WMI data.
- **Check Manually**: Run `wmic csproduct get name` to verify if Windows itself can see the data. If `wmic` fails, `lshw-windows-emulator` will also fail.

## 3. Firewall/Network Issues (Remote Execution)

**Symptoms:**

- "RPC server is unavailable" errors.
- Timeouts when running scripts remotely (e.g., via Migasfree agent).

**Causes:**

- Windows Firewall blocking WMI/RPC traffic.
- DCOM disabled.

**Solutions:**

- **Allow WMI through Firewall**:

  ```powershell
  netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes
  ```

## 4. Python Environment Issues

**Symptoms:**

- `ModuleNotFoundError: No module named 'wmi'`
- `ImportError: No module named 'win32com'`

**Causes:**

- Missing dependencies.
- Incompatible Python version (Project requires Python 3.6+).

**Solutions:**

- **Install Dependencies**:

  As this project uses `pyproject.toml`, install dependencies directly from the source:

  ```bash
  pip install .
  ```

- **Verify Python Version**:

  ```bash
  python --version
  ```

## 5. Reporting Bugs

If you encounter an issue not listed here, please generate a debug log:

```bash
# Windows
set logging_level=DEBUG
lshw -json > inventory_debug.json
```

Submit the `inventory_debug.json` along with the error log to the development team.
