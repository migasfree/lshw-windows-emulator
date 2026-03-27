from unittest.mock import MagicMock

from lshw.classes.ide import Ide


def test_ide_basic(mock_wmi_connection):
    mock_assoc = MagicMock()
    mock_assoc.antecedent = '\\\\.\\root\\cimv2:Win32_IDEController.DeviceID="PCI\\\\VEN_8086"'
    mock_assoc.dependent = '\\\\.\\root\\cimv2:Win32_IDEController.DeviceID="PCI\\\\SECONDARY"'
    mock_wmi_connection.Win32_IDEControllerdevice.return_value = [mock_assoc]

    mock_ide_primary = MagicMock()
    mock_ide_primary.PNPDeviceID = 'PCI\\VEN_8086'
    mock_ide_primary.Description = 'IDE Ctrl'
    mock_ide_primary.Caption = 'Intel IDE'
    mock_ide_primary.Manufacturer = 'Intel'

    mock_ide_secondary = MagicMock()
    mock_ide_secondary.PNPDeviceID = 'PCI\\SECONDARY'
    mock_ide_secondary.Description = 'Sec IDE'
    mock_ide_secondary.Caption = 'Sec Intel IDE'
    mock_ide_secondary.Manufacturer = 'Intel'

    def mock_query(wql):
        if 'PCI\\VEN_8086' in wql:
            return [mock_ide_primary]
        if 'PCI\\SECONDARY' in wql:
            return [mock_ide_secondary]
        return []

    mock_wmi_connection.query.side_effect = mock_query

    ide = Ide()
    result = ide.format_data()

    assert len(result) == 1
    assert result[0].product == 'Intel IDE'
    assert result[0].pnpdeviceid == 'PCI\\VEN_8086'


def test_ide_exception(mocker, mock_wmi_connection):
    mock_wmi_connection.Win32_IDEControllerdevice.side_effect = AttributeError('WMI Failure')

    ide = Ide()
    result = ide.format_data()

    assert len(result) == 0
