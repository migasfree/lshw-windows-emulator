from unittest.mock import MagicMock

from lshw.classes.usb import Usb


def test_usb_basic(mock_wmi_connection):
    mock_usb = MagicMock()
    mock_usb.PNPDeviceID = 'PNP_USB'
    mock_usb.DeviceID = 'DEV_USB'
    mock_usb.Description = 'USB Cont'
    mock_usb.Manufacturer = 'Vendor'

    mock_wmi_connection.Win32_USBController.return_value = [mock_usb]

    u = Usb()
    result = u.format_data()

    assert len(result) == 1
    assert result[0].description == 'USB Cont'
    assert result[0].vendor == 'Vendor'
    assert result[0].pnpdeviceid == 'PNP_USB'


def test_usb_children(mocker, mock_wmi_connection):
    from lshw.classes.hardware import Hardware
    from lshw.classes.usb_device import UsbDevice

    mock_usb = MagicMock()
    mock_usb.PNPDeviceID = 'PNP_USB'
    mock_wmi_connection.Win32_USBController.return_value = [mock_usb]

    mocker.patch.object(UsbDevice, 'format_data', return_value=[Hardware(id='usb_mouse')])

    u = Usb()
    result = u.format_data(children=True)

    assert len(result) == 1
    assert len(result[0].children) == 1
    assert result[0].children[0].id == 'usb_mouse'
