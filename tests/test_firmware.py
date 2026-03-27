from unittest.mock import MagicMock

from lshw.classes.firmware import Firmware


def test_firmware_basic(mock_wmi_connection):
    mock_bios = MagicMock()
    mock_bios.Manufacturer = 'Vendor'
    mock_bios.ReleaseDate = '20230101'
    mock_bios.SerialNumber = '12345'
    mock_bios.BIOSVersion = ['1.0']

    # Need to make mock_wmi_connection return this for Win32_bios
    # Wait, get_hardware uses getattr(self.wmi_system, self.wmi_method)
    mock_wmi_connection.Win32_bios.return_value = [mock_bios]

    fw = Firmware()
    result = fw.format_data()

    assert len(result) == 1
    assert result[0].vendor == 'Vendor'
    assert result[0].date == '20230101'
    assert result[0].serial == '12345'
    assert result[0].version == '1.0'
