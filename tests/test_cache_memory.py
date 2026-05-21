from unittest.mock import MagicMock

from lshw.classes.cache_memory import CacheMemory


def test_cache_memory_basic(mock_wmi_connection):
    """Test standard CacheMemory parsing and scale conversion."""
    mock_cache = MagicMock()
    mock_cache.DeviceID = 'Cache Memory 0'
    mock_cache.InstalledSize = 256  # 256 KB
    mock_cache.Level = 3  # L1
    mock_cache.Purpose = 'L1 Cache'
    mock_cache.Status = 'OK'

    mock_wmi_connection.Win32_CacheMemory.return_value = [mock_cache]

    cache = CacheMemory()
    result = cache.format_data()

    assert len(result) == 1
    c = result[0]
    assert c.id == 'cache:0'
    assert c.class_ == 'memory'
    assert c.size == 256 * 1024
    assert c.description == 'L1 cache'
    assert c.product == 'L1 Cache'
    assert c.slot == 'Cache Memory 0'


def test_cache_memory_level_mapping(mock_wmi_connection):
    """Test mapping of Level attribute (L1, L2, L3)."""
    mock_l1 = MagicMock()
    mock_l1.DeviceID = 'L1'
    mock_l1.InstalledSize = 64
    mock_l1.Level = 3

    mock_l2 = MagicMock()
    mock_l2.DeviceID = 'L2'
    mock_l2.InstalledSize = 512
    mock_l2.Level = 4

    mock_l3 = MagicMock()
    mock_l3.DeviceID = 'L3'
    mock_l3.InstalledSize = 8192
    mock_l3.Level = 5

    mock_wmi_connection.Win32_CacheMemory.return_value = [mock_l1, mock_l2, mock_l3]

    cache = CacheMemory()
    result = cache.format_data()

    assert len(result) == 3
    assert result[0].description == 'L1 cache'
    assert result[1].description == 'L2 cache'
    assert result[2].description == 'L3 cache'
