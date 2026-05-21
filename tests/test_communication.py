from unittest.mock import MagicMock

from lshw.classes.communication import Communication


def test_communication_basic(mock_wmi_connection):
    mock_serial = MagicMock()
    mock_serial.DeviceID = 'COM1'
    mock_serial.Description = 'Communications Port'
    mock_serial.Name = 'Communications Port (COM1)'
    mock_serial.ProviderType = 'Standard Port'
    mock_serial.MaxBaudRate = 115200
    mock_serial.Caption = 'COM1 Port'
    # Set these to None to test the fallback logic to ProviderType and DeviceID
    mock_serial.Manufacturer = None
    mock_serial.ProviderName = None
    mock_serial.AttachedTo = None

    def query_side_effect(wql):
        if 'Win32_SerialPort' in wql:
            return [mock_serial]
        return []

    mock_wmi_connection.query.side_effect = query_side_effect

    comm = Communication()
    result = comm.format_data()

    assert len(result) == 1
    assert result[0].id == 'communication:0'
    assert result[0].description == 'Communications Port'
    assert result[0].product == 'Communications Port (COM1)'
    assert result[0].vendor == 'Standard Port'
    assert result[0].logicalname == 'COM1'
    assert result[0].clock == 115200


def test_communication_modem(mock_wmi_connection):
    mock_modem = MagicMock()
    mock_modem.DeviceID = 'Modem0'
    mock_modem.Description = 'Standard 56000 bps Modem'
    mock_modem.Name = '56k Modem Device'
    mock_modem.AttachedTo = 'COM3'
    mock_modem.MaxBaudRate = 56000
    mock_modem.Caption = 'Modem on COM3'
    mock_modem.Manufacturer = 'Generic Corp'

    def query_side_effect(wql):
        if 'Win32_POTSModem' in wql:
            return [mock_modem]
        return []

    mock_wmi_connection.query.side_effect = query_side_effect

    comm = Communication()
    result = comm.format_data()

    assert len(result) == 1
    assert result[0].id == 'communication:0'
    assert result[0].description == 'Standard 56000 bps Modem'
    assert result[0].product == '56k Modem Device'
    assert result[0].vendor == 'Generic Corp'
    assert result[0].logicalname == 'COM3'
    assert result[0].clock == 56000
