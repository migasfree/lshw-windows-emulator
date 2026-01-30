from unittest.mock import MagicMock

from lshw.classes.processor import Processor


def test_processor_wmi_method(mock_wmi_connection):
    """Test that Processor class uses correct WMI method."""
    cpu = Processor()
    assert cpu.wmi_method == 'Win32_processor'


def test_processor_properties(mock_wmi_connection):
    """Test that Processor requests correct WMI properties."""
    cpu = Processor()
    expected_props = [
        'Manufacturer',
        'Name',
        'Description',
        'SocketDesignation',
        'DataWidth',
        'MaxClockSpeed',
    ]
    assert cpu.properties_to_get == expected_props


def test_processor_format_data(mock_wmi_connection):
    """Test data formatting with mocked WMI response."""
    # Setup mock data for two CPUs
    mock_cpu1 = MagicMock()
    mock_cpu1.Manufacturer = 'Intel'
    mock_cpu1.Name = 'Intel Core i7'
    mock_cpu1.Description = 'Intel64 Family 6'
    mock_cpu1.SocketDesignation = 'CPU 1'
    mock_cpu1.DataWidth = 64
    mock_cpu1.MaxClockSpeed = 3200

    mock_cpu2 = MagicMock()
    mock_cpu2.Manufacturer = 'Intel'
    mock_cpu2.Name = 'Intel Core i7'
    mock_cpu2.Description = 'Intel64 Family 6'
    mock_cpu2.SocketDesignation = 'CPU 2'
    mock_cpu2.DataWidth = 64
    mock_cpu2.MaxClockSpeed = 3200

    # Mock the WMI query response
    mock_wmi_connection.Win32_processor.return_value = [mock_cpu1, mock_cpu2]

    cpu = Processor()
    result = cpu.format_data()

    # Verify results
    assert len(result) == 2

    # Check CPU 1
    assert result[0].id == 'cpu:0'
    assert result[0].vendor == 'Intel'
    assert result[0].product == 'Intel Core i7'
    assert result[0].slot == 'CPU 1'
    assert result[0].width == 64
    assert result[0].clock == 3200

    # Check CPU 2
    assert result[1].id == 'cpu:1'
    assert result[1].slot == 'CPU 2'


def test_processor_handles_missing_data(mock_wmi_connection):
    """Test robust handling when WMI properties are missing."""
    mock_cpu = MagicMock()
    # Only Name is available, others missing causing AttributeError on access
    mock_cpu.Name = 'Generic CPU'
    del mock_cpu.Manufacturer

    mock_wmi_connection.Win32_processor.return_value = [mock_cpu]

    cpu = Processor()
    result = cpu.format_data()

    assert len(result) == 1
    assert result[0].product == 'Generic CPU'
    assert result[0].vendor == 'Unknown'  # Default error value
