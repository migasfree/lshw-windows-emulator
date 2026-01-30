from unittest.mock import MagicMock

from lshw.classes.pci import Pci
from lshw.classes.physical_disk import PhysicalDisk


def test_disk_duplication(mock_wmi_connection):
    """
    Test that disks are not duplicated in the hierarchy.
    Currently, PhysicalDisk is a child of both Pci and Ide.
    """
    # 1. Setup Mock for Pci (Win32_Bus)
    mock_bus = MagicMock()
    mock_bus.Caption = 'PCI Bus'
    mock_bus.Description = 'PCI Bus'
    mock_bus.DeviceID = 'PCI_BUS_0'
    mock_wmi_connection.Win32_Bus.return_value = [mock_bus]

    # 2. Setup Mock for Ide (Win32_IDEController)
    mock_ide_assoc = MagicMock()
    mock_ide_assoc.antecedent = '\\\\.\\root\\cimv2:Win32_IDEController.DeviceID="PCI\\VEN_8086&DEV_7111&SUBSYS_00000000&REV_01\\3&267A6103&0&39"'
    mock_ide_assoc.dependent = '\\\\.\\root\\cimv2:Win32_PNPEntity.DeviceID="IDE\\DISK_VBOX_HARDDISK___________________________1.0_____\\4&29D9344&0&0.0.0"'
    mock_wmi_connection.Win32_IDEControllerdevice.return_value = [mock_ide_assoc]

    mock_ide = MagicMock()
    mock_ide.Caption = 'Standard IDE Controller'
    mock_ide.Description = 'Standard IDE Controller'
    mock_ide.Manufacturer = 'Standard'
    mock_ide.PNPDeviceID = 'PCI\\VEN_8086&DEV_7111&SUBSYS_00000000&REV_01\\3&267A6103&0&39'
    mock_ide.DeviceID = 'PCI\\VEN_8086&DEV_7111&SUBSYS_00000000&REV_01\\3&267A6103&0&39'

    def mock_query(wql):
        if 'Win32_IDEController' in wql and 'PCI\\VEN' in wql:
            return [mock_ide]
        if 'Win32_PNPEntity' in wql and 'IDE\\DISK' in wql:
            mock_disk_entity = MagicMock()
            mock_disk_entity.PNPDeviceID = (
                'IDE\\DISK_VBOX_HARDDISK___________________________1.0_____\\4&29D9344&0&0.0.0'
            )
            # Simulating associators for Win32_DiskDrive
            mock_disk_entity.associators.return_value = [MagicMock()]
            return [mock_disk_entity]
        if 'Win32_diskdrive' in wql:
            return [mock_disk]
        return []

    mock_wmi_connection.query.side_effect = mock_query

    # 3. Setup Mock for PhysicalDisk (Win32_DiskDrive)
    mock_disk = MagicMock()
    mock_disk.Caption = 'VBOX HARDDISK'
    mock_disk.Description = 'Disk Drive'
    mock_disk.DeviceID = '\\\\.\\PHYSICALDRIVE0'
    mock_disk.PNPDeviceID = 'IDE\\DISK_VBOX_HARDDISK___________________________1.0_____\\4&29D9344&0&0.0.0'
    mock_disk.Index = 0
    mock_disk.Size = '1000000000'
    mock_disk.Manufacturer = 'VirtualBox'
    mock_wmi_connection.Win32_Diskdrive.return_value = [mock_disk]

    # Run Pci.format_data(children=True)
    # Pci -> Ide -> PhysicalDisk
    # and Pci -> PhysicalDisk
    pci = Pci()
    result = pci.format_data(children=True)

    # Inspect the hierarchy
    pci_node = result[0]

    import json

    # Convert to dict for easier printing
    print(json.dumps(pci_node.to_dict(), indent=2))

    # Count how many times 'VBOX HARDDISK' appears in the whole tree
    def count_product(node, name):
        count = 1 if node.product == name else 0
        for child in node.children:
            count += count_product(child, name)
        return count

    disk_count = count_product(pci_node, 'VBOX HARDDISK')

    # Currently it should be 1 because of the fix
    assert disk_count == 1, f'Expected 1 disk, but found {disk_count}'


def test_physical_disk_basic(mock_wmi_connection):
    """
    Test basic PhysicalDisk functionality.
    """
    mock_disk = MagicMock()
    mock_disk.Caption = 'Basic Disk'
    mock_disk.Description = 'Description'
    mock_disk.DeviceID = 'DEV_0'
    mock_disk.PNPDeviceID = 'PNP_0'
    mock_disk.Index = 0
    mock_disk.Size = '50000000000'
    mock_disk.Manufacturer = 'Vendor'
    mock_wmi_connection.Win32_Diskdrive.return_value = [mock_disk]

    disk_class = PhysicalDisk()
    result = disk_class.format_data()

    assert len(result) == 1
    assert result[0].product == 'Basic Disk'
    assert result[0].size == 50000000000
    assert result[0].vendor == 'Vendor'


def test_physical_disk_multiple(mock_wmi_connection):
    """
    Test detection of multiple physical disks.
    """
    mock_disk1 = MagicMock()
    mock_disk1.Caption = 'Disk 1'
    mock_disk1.Description = 'Desc 1'
    mock_disk1.DeviceID = 'DEV_1'
    mock_disk1.PNPDeviceID = 'PNP_1'
    mock_disk1.Index = 0
    mock_disk1.Size = '100'
    mock_disk1.Manufacturer = 'M1'

    mock_disk2 = MagicMock()
    mock_disk2.Caption = 'Disk 2'
    mock_disk2.Description = 'Desc 2'
    mock_disk2.DeviceID = 'DEV_2'
    mock_disk2.PNPDeviceID = 'PNP_2'
    mock_disk2.Index = 1
    mock_disk2.Size = '200'
    mock_disk2.Manufacturer = 'M2'

    mock_wmi_connection.Win32_Diskdrive.return_value = [mock_disk1, mock_disk2]

    disk_class = PhysicalDisk()
    result = disk_class.format_data()

    assert len(result) == 2
    assert result[0].product == 'Disk 1'
    assert result[1].product == 'Disk 2'
    assert result[0].size == 100
    assert result[1].size == 200


def test_physical_disk_size_parsing_error(mock_wmi_connection):
    """
    Test that invalid size values don't crash the application.
    """
    mock_disk = MagicMock()
    mock_disk.Caption = 'Broken Size Disk'
    mock_disk.Description = 'Desc'
    mock_disk.DeviceID = 'DEV_0'
    mock_disk.PNPDeviceID = 'PNP_0'
    mock_disk.Index = 0
    mock_disk.Size = 'not-a-number'
    mock_disk.Manufacturer = 'M'
    mock_wmi_connection.Win32_Diskdrive.return_value = [mock_disk]

    disk_class = PhysicalDisk()
    result = disk_class.format_data()

    assert len(result) == 1
    assert result[0].size == 0


def test_physical_disk_dev_id_filtering(mock_wmi_connection):
    """
    Test filtering by dev_id.
    """
    mock_disk = MagicMock()
    mock_disk.Caption = 'Filtered Disk'
    mock_disk.Description = 'Desc'
    mock_disk.DeviceID = 'DEV_SPECIFIC'
    mock_disk.PNPDeviceID = 'PNP_SPECIFIC'
    mock_disk.Index = 0
    mock_disk.Size = '1000'
    mock_disk.Manufacturer = 'M'

    # When dev_id is provided, get_hardware uses execute_wql_query
    # and build_wql_select. We need to mock query() for the WQL string.
    def mock_query(wql):
        if 'WHERE PNPDeviceID LIKE "%PNP_SPECIFIC%"' in wql:
            return [mock_disk]
        return []

    mock_wmi_connection.query.side_effect = mock_query

    disk_class = PhysicalDisk(dev_id='PNP_SPECIFIC')
    result = disk_class.format_data()

    assert len(result) == 1
    assert result[0].product == 'Filtered Disk'
    assert result[0].pnpdeviceid == 'PNP_SPECIFIC'
