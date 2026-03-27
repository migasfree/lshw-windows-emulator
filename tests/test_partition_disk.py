from unittest.mock import MagicMock

from lshw.classes.partition_disk import PartitionDisk


def test_partition_disk_basic(mock_wmi_connection):
    mock_pd = MagicMock()
    mock_pd.Bootable = True
    mock_pd.BootPartition = True
    mock_pd.PrimaryPartition = True
    mock_pd.DeviceID = 'Disk #0, Partition #0'
    mock_pd.PNPDeviceID = 'PNP_PART'
    mock_pd.Index = 0
    mock_pd.Size = '500'
    mock_pd.Description = 'Partition'

    mock_wmi_connection.Win32_Diskpartition.return_value = [mock_pd]

    pd = PartitionDisk()
    result = pd.format_data()

    assert len(result) == 1
    assert result[0].size == '500'
    assert result[0].pnpdeviceid == 'PNP_PART'
    assert result[0].id == 'volume:0'


def test_partition_disk_dev_id(mock_wmi_connection):
    mock_pd = MagicMock()
    mock_pd.DeviceID = 'Disk #1, Partition #0'
    mock_pd.Size = '100'
    mock_pd.PNPDeviceID = ''
    mock_pd.Index = 0

    mock_drive = MagicMock()
    mock_drive.associators.return_value = [mock_pd]

    def mock_query(wql):
        if '\\\\.\\PHYSICALDRIVE1' in wql:
            return [mock_drive]
        return []

    mock_wmi_connection.query.side_effect = mock_query

    pd = PartitionDisk(dev_id='\\\\.\\PHYSICALDRIVE1')
    result = pd.format_data()

    assert len(result) == 1
    assert result[0].deviceid == 'Disk #1, Partition #0'


def test_partition_disk_children(mocker, mock_wmi_connection):
    from lshw.classes.hardware import Hardware
    from lshw.classes.logical_disk import LogicalDisk

    mock_pd = MagicMock()
    mock_pd.DeviceID = 'Disk #0, Partition #0'
    mock_pd.PNPDeviceID = ''
    mock_pd.Index = 0
    mock_pd.Size = '0'
    mock_wmi_connection.Win32_Diskpartition.return_value = [mock_pd]

    mocker.patch.object(LogicalDisk, 'format_data', return_value=[Hardware(id='logicalvolume:2')])

    pd = PartitionDisk()
    result = pd.format_data(children=True)

    assert len(result) == 1
    assert len(result[0].children) == 1
    assert result[0].children[0].id == 'logicalvolume:2'
