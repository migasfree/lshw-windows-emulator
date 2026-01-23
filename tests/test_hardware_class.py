from unittest.mock import MagicMock

import pytest

from lshw.classes.hardware_class import HardwareClass


class ConcreteHardware(HardwareClass):
    """
    Concrete subclass for testing HardwareClass abstract base class.
    """

    def format_data(self, children=False):
        return {'test': 'data'}


def test_hardware_class_is_abstract():
    """Test that HardwareClass cannot be instantiated directly."""
    with pytest.raises(TypeError):
        HardwareClass()


def test_concrete_hardware_instantiation(mock_wmi_connection):
    """Test proper instantiation of a concrete subclass with WMI connection."""
    hw = ConcreteHardware()
    assert hw.wmi_system == mock_wmi_connection
    assert hw.format_data() == {'test': 'data'}


def test_build_wql_fields(mock_wmi_connection):
    """Test WQL field list construction."""
    hw = ConcreteHardware()
    hw.properties_to_get = ['Name', 'Description', 'DeviceID']
    assert hw.build_wql_fields() == 'Name,Description,DeviceID'


def test_build_wql_select_simple(mock_wmi_connection):
    """Test WQL SELECT statement construction."""
    hw = ConcreteHardware()
    hw.properties_to_get = ['Name', 'Status']
    wql = hw.build_wql_select(table='Win32_NetworkAdapter')
    assert wql == 'SELECT Name,Status FROM Win32_NetworkAdapter'


def test_build_wql_select_with_where(mock_wmi_connection):
    """Test WQL SELECT statement with WHERE clause."""
    hw = ConcreteHardware()
    hw.properties_to_get = ['Name']
    wql = hw.build_wql_select(table='Win32_NetworkAdapter', where_clause="State='Running'")
    assert wql == "SELECT Name FROM Win32_NetworkAdapter WHERE State='Running'"


def test_execute_wql_query(mock_wmi_connection):
    """Test executing a WQL query populates hardware_set."""
    hw = ConcreteHardware()

    # Setup mock return data
    mock_item = MagicMock()
    mock_item.Name = 'TestItem'
    mock_wmi_connection.query.return_value = [mock_item]

    hw.execute_wql_query('SELECT * FROM Win32_Test')

    # Verify interaction
    mock_wmi_connection.query.assert_called_once_with('SELECT * FROM Win32_Test')
    assert len(hw.hardware_set) == 1
    assert hw.hardware_set[0] == mock_item


def test_check_values_handles_missing_attributes(mock_wmi_connection):
    """Test that check_values handles missing attributes gracefully (logs warning)."""
    hw = ConcreteHardware()
    hw.properties_to_get = ['ExistingProp', 'MissingProp']
    hw._update_properties_to_return()

    # Mock HW item with only one property
    mock_item = MagicMock()
    mock_item.ExistingProp = 'Value'
    del mock_item.MissingProp  # Ensure specific AttributeError

    hw.hardware_set = [mock_item]

    # This should log a warning but not crash
    hw.check_values()

    result = hw.hardware_set_to_return[0]
    assert result['ExistingProp'] == 'Value'
    assert result['MissingProp'] == HardwareClass.__DESC__  # Should be default 'Unknown'


def test_validate_entity_authorized(mock_wmi_connection):
    """Test that authorized entities do not raise error."""
    hw = ConcreteHardware()
    hw._validate_entity('Win32_NetworkAdapter')  # Should not raise


def test_validate_entity_unauthorized(mock_wmi_connection):
    """Test that unauthorized entities raise ValueError."""
    hw = ConcreteHardware()
    with pytest.raises(ValueError, match='Unauthorized WMI entity: Win32_Invalid'):
        hw._validate_entity('Win32_Invalid')


def test_get_hardware_unauthorized_method(mock_wmi_connection):
    """Test that get_hardware raises ValueError for unauthorized wmi_method."""
    hw = ConcreteHardware()
    hw.wmi_method = 'UnauthorizedMethod'
    with pytest.raises(ValueError, match='Unauthorized WMI entity: UnauthorizedMethod'):
        hw.get_hardware()
