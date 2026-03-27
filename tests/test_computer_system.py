from unittest.mock import MagicMock

from lshw.classes.computer_system import ComputerSystem


def test_computer_system_basic(mock_wmi_connection):
    mock_cs = MagicMock()
    mock_cs.Model = 'MyModel'
    mock_cs.Name = 'MyName'
    mock_cs.Description = 'MyDesc'
    mock_cs.Manufacturer = 'MyVendor'
    mock_cs.NumberOfProcessors = 2
    mock_wmi_connection.Win32_computersystem.return_value = [mock_cs]

    mock_enclosure = MagicMock()
    mock_enclosure.ChassisTypes = [3]  # 3 = Desktop
    mock_wmi_connection.Win32_SystemEnclosure.return_value = [mock_enclosure]

    mock_product = MagicMock()
    mock_product.UUID = '123-456'
    mock_product.IdentifyingNumber = 'SERIAL001'
    mock_wmi_connection.Win32_Computersystemproduct.return_value = [mock_product]

    cs = ComputerSystem()
    result = cs.format_data()

    assert len(result) == 1
    assert result[0].id == 'MyName'
    assert result[0].description == 'MyDesc, Desktop'
    assert result[0].product == 'MyModel'
    assert result[0].vendor == 'MyVendor'
    assert result[0].serial == 'SERIAL001'
    assert result[0].configuration['chassis'] == 'Desktop'
    assert result[0].configuration['cpus'] == 2
    assert result[0].configuration['uuid'] == '123-456'


def test_computer_system_no_chassis(mock_wmi_connection):
    mock_cs = MagicMock()
    mock_wmi_connection.Win32_computersystem.return_value = [mock_cs]

    mock_enclosure = MagicMock()
    mock_enclosure.ChassisTypes = None
    mock_wmi_connection.Win32_SystemEnclosure.return_value = [mock_enclosure]

    mock_product = MagicMock()
    mock_wmi_connection.Win32_Computersystemproduct.return_value = [mock_product]

    cs = ComputerSystem()
    result = cs.format_data()

    assert result[0].configuration['chassis'] == 'Unknown'
