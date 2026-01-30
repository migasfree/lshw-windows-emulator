from unittest.mock import MagicMock, patch

from lshw.classes.network_card import NetworkCard


def test_network_card_query_logic(mock_wmi_connection):
    """Test NetworkCard implementation of correct WQL query logic."""
    net = NetworkCard()

    # Needs to mock platform to check query logic
    with patch('platform.release', return_value='10'), patch('platform.version', return_value='10.0.19041'):  # > 18362
        net.get_hardware()

        # Verify it used the new WHERE clause for Win 10 newer builds
        mock_wmi_connection.query.assert_called_with(
            'SELECT Speed,SystemCreationClassName,AdapterType,Autosense,Caption,MACAddress,ProductName,Manufacturer,NetConnectionID,Description,PNPDeviceID FROM Win32_NetworkAdapter WHERE (PhysicalAdapter=True)'
        )


def test_network_card_legacy_query_logic(mock_wmi_connection):
    """Test NetworkCard fallback query logic for older Windows."""
    net = NetworkCard()

    with patch('platform.release', return_value='7'):
        net.get_hardware()

        # Verify it used the legacy WHERE clause
        mock_wmi_connection.query.assert_called_with(
            'SELECT Speed,SystemCreationClassName,AdapterType,Autosense,Caption,MACAddress,ProductName,Manufacturer,NetConnectionID,Description,PNPDeviceID FROM Win32_NetworkAdapter WHERE (NOT PNPDeviceID LIKE "%ROOT%")'
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

    mock_wmi_connection.query.return_value = [mock_nic]

    net = NetworkCard()
    # Mocking get_hardware inside format_data is tricky unless we rely on wmi mocking
    # Since we mocked WMI response above, get_hardware will just populate hardware_set from it

    result = net.format_data()

    assert len(result) == 1
    nic = result[0]

    assert nic.product == 'Intel Ethernet'
    assert nic.logicalname == 'Ethernet'
    assert nic.serial == '00:11:22:33:44:55'
    assert nic.configuration['speed'] == 1000000000
    assert nic.configuration['autonegotiation'] is True
