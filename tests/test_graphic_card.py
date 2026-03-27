from unittest.mock import MagicMock

from lshw.classes.graphic_card import GraphicCard


def test_graphic_card_basic(mock_wmi_connection):
    mock_gc = MagicMock()
    mock_gc.Description = 'Desc'
    mock_gc.VideoProcessor = 'GPU'
    mock_gc.AdapterCompatibility = 'Vendor'
    mock_gc.PNPDeviceID = 'PNP_GPU'

    mock_wmi_connection.Win32_videoController.return_value = [mock_gc]

    gc = GraphicCard()
    result = gc.format_data()

    assert len(result) == 1
    assert result[0].description == 'Desc'
    assert result[0].product == 'GPU'
    assert result[0].vendor == 'Vendor'
    assert result[0].pnpdeviceid == 'PNP_GPU'
    assert result[0].width == 0
