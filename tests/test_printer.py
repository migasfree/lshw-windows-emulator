from unittest.mock import MagicMock

from lshw.classes.printer import Printer


def test_printer_basic(mock_wmi_connection):
    mock_printer = MagicMock()
    mock_printer.DeviceID = 'HP_LaserJet'
    mock_printer.Name = 'HP LaserJet Professional'
    mock_printer.Caption = 'HP Office Printer'
    mock_printer.DriverName = 'HP LaserJet Class Driver'
    mock_printer.PortName = 'USB001'
    mock_printer.Network = False
    mock_printer.Local = True

    mock_wmi_connection.query.return_value = [mock_printer]

    pr = Printer()
    result = pr.format_data()

    assert len(result) == 1
    assert result[0].id == 'printer:0'
    assert result[0].description == 'HP Office Printer'
    assert result[0].product == 'HP LaserJet Class Driver'
    assert result[0].vendor == 'HP'
    assert result[0].logicalname == 'USB001'
    assert result[0].configuration['network'] == 'false'
    assert result[0].configuration['local'] == 'true'


def test_printer_generic_driver(mock_wmi_connection):
    mock_printer = MagicMock()
    mock_printer.DeviceID = 'GenericPDF'
    mock_printer.Name = 'Microsoft Print to PDF'
    mock_printer.Caption = 'PDF Printer'
    mock_printer.DriverName = 'Microsoft PDF Printer Driver'
    mock_printer.PortName = 'PORTPROMPT:'
    mock_printer.Network = True
    mock_printer.Local = False

    mock_wmi_connection.query.return_value = [mock_printer]

    pr = Printer()
    result = pr.format_data()

    assert len(result) == 1
    assert result[0].id == 'printer:0'
    assert result[0].description == 'PDF Printer'
    assert result[0].product == 'Microsoft PDF Printer Driver'
    assert result[0].vendor == 'Software'
    assert result[0].logicalname == 'PORTPROMPT:'
    assert result[0].configuration['network'] == 'true'
    assert result[0].configuration['local'] == 'false'
