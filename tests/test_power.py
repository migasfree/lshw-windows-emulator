from unittest.mock import MagicMock

from lshw.classes.power import Power


def test_power_basic(mock_wmi_connection):
    mock_battery = MagicMock()
    mock_battery.DeviceID = 'BAT0'
    mock_battery.Description = 'Internal Battery'
    mock_battery.Name = 'Lithium Battery Pack'
    mock_battery.Manufacturer = 'VendorA'
    mock_battery.SerialNumber = 'SN12345'
    mock_battery.DesignCapacity = 50000
    mock_battery.Chemistry = 'LION'

    def query_side_effect(wql):
        if 'Win32_Battery' in wql:
            return [mock_battery]
        return []

    mock_wmi_connection.query.side_effect = query_side_effect

    pw = Power()
    result = pw.format_data()

    assert len(result) == 1
    assert result[0].id == 'power:0'
    assert result[0].description == 'Internal Battery'
    assert result[0].product == 'Lithium Battery Pack'
    assert result[0].vendor == 'VendorA'
    assert result[0].serial == 'SN12345'
    assert result[0].capacity == 50000
    assert result[0].configuration['chemistry'] == 'LION'


def test_power_multiple_devices(mock_wmi_connection):
    mock_battery = MagicMock()
    mock_battery.DeviceID = 'BAT0'
    mock_battery.Description = 'Internal Battery'
    mock_battery.Name = 'Lithium Battery'
    mock_battery.Manufacturer = 'VendorA'
    mock_battery.SerialNumber = 'SN123'
    mock_battery.DesignCapacity = '50000'
    mock_battery.Chemistry = 'LION'

    mock_ups = MagicMock()
    mock_ups.DeviceID = 'UPS0'
    mock_ups.Description = 'Uninterruptible Power Supply'
    mock_ups.Name = 'UPS Device'
    mock_ups.Manufacturer = 'VendorB'
    mock_ups.SerialNumber = 'SN999'
    mock_ups.DesignCapacity = None
    mock_ups.Chemistry = None

    def query_side_effect(wql):
        if 'Win32_Battery' in wql:
            return [mock_battery]
        if 'Win32_UninterruptiblePowerSupply' in wql:
            return [mock_ups]
        return []

    mock_wmi_connection.query.side_effect = query_side_effect

    pw = Power()
    result = pw.format_data()

    assert len(result) == 2
    assert result[0].id == 'power:0'
    assert result[0].product == 'Lithium Battery'
    assert result[0].capacity == 50000

    assert result[1].id == 'power:1'
    assert result[1].product == 'UPS Device'
    assert result[1].capacity == 0
