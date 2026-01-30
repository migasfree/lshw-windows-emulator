from unittest.mock import MagicMock

from lshw.classes.physical_memory import PhysicalMemory


def test_physical_memory_format_data(mock_wmi_connection):
    """Test PhysicalMemory WMI data formatting."""
    # Setup mock data for one memory stick
    mock_mem = MagicMock()
    mock_mem.Tag = 'Physical Memory 0'
    mock_mem.DeviceLocator = 'DIMM 1'
    mock_mem.Capacity = 8589934592
    mock_mem.Speed = 2400
    mock_mem.MemoryType = 24  # DDR3 (example value)
    mock_mem.DataWidth = 64

    mock_wmi_connection.Win32_physicalMemory.return_value = [mock_mem]

    mem = PhysicalMemory()
    result = mem.format_data()

    # format_data for default memory returns a List[Hardware]
    from lshw.classes.hardware import Hardware

    assert isinstance(result, list)
    assert len(result) == 1
    mem_container = result[0]

    assert isinstance(mem_container, Hardware)
    assert mem_container.id == 'memory:0'
    assert mem_container.class_ == 'memory'

    children = mem_container.children
    assert len(children) == 1

    bank = children[0]
    assert bank.id == 'bank:0'  # Derived from "Tag"
    assert bank.description == 'Physical Memory 0'
    assert bank.size == 8589934592
    assert bank.product == 24
    assert bank.clock == 2400


def test_physical_memory_handles_missing_tag(mock_wmi_connection):
    """Test handling when 'Tag' property is missing."""
    mock_mem = MagicMock()
    mock_mem.DeviceLocator = 'DIMM 1'
    # Tag is missing
    del mock_mem.Tag

    mock_wmi_connection.Win32_physicalMemory.return_value = [mock_mem]

    mem = PhysicalMemory()
    result = mem.format_data()

    assert isinstance(result, list)
    bank = result[0].children[0]
    # Should use default ID if Tag is missing logic works, or fallback
    assert bank.id == 'bank:n'  # Derived from last char of "Unknown" fallback
    assert bank.description == 'Unknown'


def test_physical_memory_fallback_virtualbox(mock_wmi_connection):
    """
    Test fallback to Win32_ComputerSystem when Win32_PhysicalMemory is empty.
    This simulates VirtualBox behavior.
    """
    # Win32_PhysicalMemory returns nothing
    mock_wmi_connection.Win32_physicalMemory.return_value = []

    # Win32_ComputerSystem returns TotalPhysicalMemory
    mock_system = MagicMock()
    mock_system.TotalPhysicalMemory = 16 * 1024 * 1024 * 1024  # 16 GB
    mock_wmi_connection.Win32_ComputerSystem.return_value = [mock_system]

    mem = PhysicalMemory()
    result = mem.format_data()

    assert isinstance(result, list)
    assert len(result) == 1
    mem_container = result[0]

    # Should have one child (the system memory)
    assert len(mem_container.children) == 1
    bank = mem_container.children[0]

    assert bank.id == 'bank:0'
    assert bank.description == 'System Memory'
    assert bank.size == 16 * 1024 * 1024 * 1024
    assert bank.slot == 'System Board'
