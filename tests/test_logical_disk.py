from unittest.mock import MagicMock

from lshw.classes.logical_disk import LogicalDisk


def test_logical_disk_basic(mock_wmi_connection):
    mock_ld = MagicMock()
    mock_ld.Caption = 'C:'
    mock_ld.Name = 'Local Disk'
    mock_ld.Description = 'desc'
    mock_ld.FileSystem = 'NTFS'
    mock_ld.VolumeName = 'C:'
    mock_ld.Size = '1000'
    mock_ld.DeviceID = 'C:'

    mock_wmi_connection.Win32_LogicalDisk.return_value = [mock_ld]

    ld = LogicalDisk()
    result = ld.format_data()

    assert len(result) == 1
    assert result[0].logicalname == 'C:'
    assert result[0].capacity == '1000'
    assert result[0].configuration['mount.fstype'] == 'NTFS'
    assert result[0].id == 'logicalvolume:2'  # 'C' is index 2


def test_logical_disk_with_dev_id(mock_wmi_connection):
    mock_ld = MagicMock()
    mock_ld.DeviceID = 'D:'

    mock_part = MagicMock()
    mock_part.associators.return_value = [mock_ld]

    def mock_query(wql):
        if 'DeviceID="Disk #0, Partition #0"' in wql:
            return [mock_part]
        return []

    mock_wmi_connection.query.side_effect = mock_query

    ld = LogicalDisk(dev_id='Disk #0, Partition #0')
    result = ld.format_data()

    assert len(result) == 1
    assert result[0].deviceid == 'D:'


def test_logical_disk_direct_association(mock_wmi_connection):
    mock_assoc = MagicMock()
    mock_assoc.Antecedent = MagicMock()
    mock_assoc.Antecedent.DeviceID = 'Disk #0, Partition #0'
    mock_assoc.Dependent = MagicMock()
    mock_assoc.Dependent.DeviceID = 'E:'

    mock_ld = MagicMock()
    mock_ld.Caption = 'E:'
    mock_ld.Name = 'Volume'
    mock_ld.Description = 'desc'
    mock_ld.FileSystem = 'NTFS'
    mock_ld.VolumeName = 'E:'
    mock_ld.Size = '2000'
    mock_ld.DeviceID = 'E:'

    mock_wmi_connection.Win32_LogicalDiskToPartition.return_value = [mock_assoc]
    mock_wmi_connection.query.return_value = [mock_ld]

    ld = LogicalDisk(dev_id='Disk #0, Partition #0')
    result = ld.format_data()

    assert len(result) == 1
    assert result[0].deviceid == 'E:'
    assert result[0].capacity == '2000'
