from unittest.mock import MagicMock, patch

from lshw.classes.network_card import NetworkCard


def test_network_card_query_logic(mock_wmi_connection):
    """Test NetworkCard implementation of correct WQL query logic."""
    net = NetworkCard()

    # Needs to mock platform to check query logic
    with patch('platform.release', return_value='10'), patch('platform.version', return_value='10.0.19041'):  # > 18362
        net.get_hardware()

        # Verify it used the new WHERE clause for Win 10 newer builds
        mock_wmi_connection.query.assert_any_call(
            'SELECT Speed,SystemCreationClassName,AdapterType,Autosense,Caption,MACAddress,ProductName,Manufacturer,NetConnectionID,Description,PNPDeviceID,Index,NetConnectionStatus,ServiceName FROM Win32_NetworkAdapter WHERE (PhysicalAdapter=True)'
        )


def test_network_card_legacy_query_logic(mock_wmi_connection):
    """Test NetworkCard fallback query logic for older Windows."""
    net = NetworkCard()

    with patch('platform.release', return_value='7'):
        net.get_hardware()

        # Verify it used the legacy WHERE clause
        mock_wmi_connection.query.assert_any_call(
            'SELECT Speed,SystemCreationClassName,AdapterType,Autosense,Caption,MACAddress,ProductName,Manufacturer,NetConnectionID,Description,PNPDeviceID,Index,NetConnectionStatus,ServiceName FROM Win32_NetworkAdapter WHERE (NOT PNPDeviceID LIKE "%ROOT%")'
        )


def test_network_card_format_data(mock_wmi_connection):
    """Test formatting of NetworkCard data."""
    mock_nic = MagicMock()
    mock_nic.Description = 'Intel Ethernet'
    mock_nic.Manufacturer = 'Intel'
    mock_nic.NetConnectionID = 'Ethernet'
    mock_nic.MACAddress = '00:11:22:33:44:55'
    mock_nic.PNPDeviceID = 'PCI\\VEN_8086'
    mock_nic.Autosense = True
    mock_nic.Speed = 1000000000
    mock_nic.Index = 1
    mock_nic.NetConnectionStatus = 2
    mock_nic.ServiceName = 'e1dexpress'

    mock_config = MagicMock()
    mock_config.Index = 1
    mock_config.IPAddress = ['192.168.1.50']

    def query_side_effect(wql):
        if 'Win32_NetworkAdapterConfiguration' in wql:
            return [mock_config]
        if 'Win32_NetworkAdapter' in wql:
            return [mock_nic]
        return []

    mock_wmi_connection.query.side_effect = query_side_effect

    net = NetworkCard()
    result = net.format_data()

    assert len(result) == 1
    nic = result[0]

    assert nic.product == 'Intel Ethernet'
    assert nic.logicalname == 'Ethernet'
    assert nic.serial == '00:11:22:33:44:55'
    assert nic.configuration['speed'] == 1000000000
    assert nic.configuration['autonegotiation'] is True
    assert nic.configuration['driver'] == 'e1dexpress'
    assert nic.configuration['link'] == 'yes'
    assert nic.configuration['ip'] == '192.168.1.50'
