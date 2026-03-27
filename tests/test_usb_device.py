from unittest.mock import MagicMock

from lshw.classes.usb_device import UsbDevice


def test_usb_device_basic(mock_wmi_connection):
    mock_assoc = MagicMock()
    mock_assoc.antecedent = 'Win32_USBController.DeviceID="USB\\\\ROOT_HUB"'
    mock_assoc.dependent = 'Win32_PNPEntity.DeviceID="USB\\\\VID_1234"'
    mock_wmi_connection.Win32_USBControllerdevice.return_value = [mock_assoc]

    mock_pnp = MagicMock()
    mock_pnp.Caption = 'USB Device'
    mock_pnp.Description = 'Mouse compatible con HID'
    mock_pnp.DeviceID = 'DEV_USB'
    mock_pnp.PNPDeviceID = 'USB\\VID_1234'

    def mock_query(wql):
        if 'USB\\VID_1234' in wql:
            return [mock_pnp]
        return []

    mock_wmi_connection.query.side_effect = mock_query

    ud = UsbDevice()
    result = ud.format_data()

    assert len(result) == 1
    assert result[0].id == 'usb_mouse'
    assert result[0].description == 'Mouse compatible con HID'
    assert result[0].pnpdeviceid == 'USB\\VID_1234'
    assert result[0].parent_pnpdeviceid == 'USB\\ROOT_HUB'


def test_usb_device_excluded(mock_wmi_connection):
    mock_assoc = MagicMock()
    mock_assoc.antecedent = 'Win32_USBController.DeviceID="USB\\\\ROOT_HUB"'
    mock_assoc.dependent = 'Win32_PNPEntity.DeviceID="USB\\\\VID_1234"'
    mock_wmi_connection.Win32_USBControllerdevice.return_value = [mock_assoc]

    mock_pnp = MagicMock()
    mock_pnp.Caption = 'USB 2.0 Root Hub'  # This should be excluded

    def mock_query(wql):
        return [mock_pnp]

    mock_wmi_connection.query.side_effect = mock_query

    ud = UsbDevice()
    result = ud.format_data()

    assert len(result) == 0
