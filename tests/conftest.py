import sys
import types
from unittest.mock import MagicMock

import pytest

# Create a mock wmi module
mock_wmi = types.ModuleType('wmi')
mock_wmi.WMI = MagicMock()
sys.modules['wmi'] = mock_wmi

# Now import hardware classes which depend on wmi
from lshw.classes.hardware_class import WMIConnection  # noqa: E402


@pytest.fixture(autouse=True)
def mock_wmi_connection():
    """
    Mock the WMI connection singleton.
    This ensures that WMIConnection.get_instance() always returns a mock
    and resets the singleton instance before each test.
    """
    # Reset singleton instance
    WMIConnection._instance = None

    # Setup mock
    mock_connection = MagicMock()
    mock_wmi.WMI.return_value = mock_connection

    return mock_connection
