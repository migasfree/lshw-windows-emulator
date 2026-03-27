from unittest.mock import MagicMock

from lshw.classes.sound_device import SoundDevice


def test_sound_device_basic(mock_wmi_connection):
    mock_sd = MagicMock()
    mock_sd.PNPDeviceID = 'PNP_SOUND'
    mock_sd.DeviceID = 'DEV_SOUND'
    mock_sd.Manufacturer = 'Vendor'

    mock_wmi_connection.Win32_SoundDevice.return_value = [mock_sd]

    sd = SoundDevice()
    result = sd.format_data()

    assert len(result) == 1
    assert result[0].product == 'Vendor'
    assert result[0].pnpdeviceid == 'PNP_SOUND'
    assert result[0].deviceid == 'DEV_SOUND'
