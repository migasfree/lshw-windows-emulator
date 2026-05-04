# 🛠️ Admin Troubleshooting Guide

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

- Minimum WMI implementation (e.g., Windows Home editions).
- Missing drivers for specific hardware components.
- Virtual Machine environments masking physical hardware details.

**Solutions:**

- **Update Drivers**: Ensure all chipset and manufacturer drivers are installed. Generic Microsoft drivers may not expose full WMI data.
- **Check Manually**: Run `wmic csproduct get name` in a terminal. If `wmic` fails, `lshw-windows-emulator` will also fail.

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

  ```bash
  pip install .
  ```

- **Verify Python Version**:

  ```bash
  python --version
  ```

## 5. WMI Database Corruption

**Symptoms:**

- Script hangs indefinitely on queries or returns severe COM errors.
- Any WMI command like `wmic csproduct get name` fails with an inconsistent state message.

**Solutions:**

- **Check WMI Repository Consistency**: Run the following in an administrative prompt:

  ```powershell
  winmgmt /verifyrepository
  ```

  If the repository is inconsistent, attempt to salvage it:

  ```powershell
  winmgmt /salvagerepository
  ```

- **Reset WMI Repository**: If salvaging fails, reset WMI to its default state:

  ```powershell
  winmgmt /resetrepository
  ```

- **Force Rebuild WMI**: In extreme scenarios where WMI is completely broken:

  ```cmd
  net stop winmgmt /y
  rd /s /q "%windir%\System32\wbem\Repository"
  net start winmgmt
  ```

## 6. Reporting Bugs

If you encounter an issue not listed here, please generate a debug log:

```powershell
# Windows
set logging_level=DEBUG
lshw -json > inventory_debug.json
```

Submit the `inventory_debug.json` alongside the error log to the development team or open a GitHub Issue.

---
> [!NOTE]
> This guide follows the **Diátaxis How-To Quadrant**, focusing on specific goal-oriented tasks.
