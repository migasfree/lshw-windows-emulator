from unittest.mock import MagicMock

from lshw.classes.cd_rom import CdRom


def test_cd_rom_basic(mock_wmi_connection):
    mock_cd = MagicMock()
    mock_cd.DeviceID = 'DEV_CD'
    mock_cd.PNPDeviceID = 'PNP_CD'
    mock_cd.Manufacturer = 'Vendor'
    mock_cd.Name = 'Product'
    mock_cd.Description = 'Desc'
    mock_cd.Drive = 'D:'
    mock_cd.MediaLoaded = True

    mock_wmi_connection.Win32_cdromdrive.return_value = [mock_cd]

    cd = CdRom()
    result = cd.format_data()

    assert len(result) == 1
    assert result[0].logicalname == 'D:'
    assert result[0].product == 'Product'
    assert result[0].vendor == 'Vendor'
    assert result[0].pnpdeviceid == 'PNP_CD'
    assert result[0].configuration['status'] == 'loaded disc'


def test_cd_rom_no_media(mock_wmi_connection):
    mock_cd = MagicMock()
    mock_cd.MediaLoaded = False

    mock_wmi_connection.Win32_cdromdrive.return_value = [mock_cd]

    cd = CdRom()
    result = cd.format_data()

    assert result[0].configuration['status'] == 'no disc'


def test_cd_rom_dev_id(mock_wmi_connection):
    mock_cd = MagicMock()
    mock_cd.PNPDeviceID = 'PNP_SPECIFIC'

    def mock_query(wql):
        if 'PNP_SPECIFIC' in wql:
            return [mock_cd]
        return []

    mock_wmi_connection.query.side_effect = mock_query

    cd = CdRom(dev_id='PNP_SPECIFIC')
    result = cd.format_data()

    assert len(result) == 1
    assert result[0].pnpdeviceid == 'PNP_SPECIFIC'
