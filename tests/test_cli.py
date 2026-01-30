import json
from unittest.mock import MagicMock, patch

import pytest

from lshw.__main__ import main
from lshw.classes.hardware import Hardware


def test_json_output_serialization(capsys):
    """
    Test that lshw -j produces valid JSON output even when format_data returns Hardware objects.
    This specifically checks for the regression where Hardware objects were not serializable.
    """
    # Mock argv
    test_argv = ['-j']

    # Mock HardwareClass factory and instance
    # We need to patch where main imports HardwareClass, or patch the class itself if it was already imported
    with patch('lshw.__main__.HardwareClass') as mock_hardware_class:
        # User requests full system info by default
        mock_instance = MagicMock()

        # Create a dummy Hardware object
        hw = Hardware(id='test-pc', product='Test Computer', description='A test computer')

        # format_data returns a list of Hardware objects
        mock_instance.format_data.return_value = [hw]

        # Setup the factory to return a class that returns our mock instance
        mock_hardware_class.factory.return_value = MagicMock(return_value=mock_instance)

        # Run main
        exit_code = main(test_argv)

        # Assert exit code 0
        assert exit_code == 0

        # Capture stdout
        captured = capsys.readouterr()

        # Verify JSON is valid
        try:
            output_json = json.loads(captured.out)
        except json.JSONDecodeError:
            pytest.fail('Output is not valid JSON')

        # Verify content
        assert isinstance(output_json, list)
        assert len(output_json) == 1
        assert output_json[0]['id'] == 'test-pc'
        assert output_json[0]['product'] == 'Test Computer'


def test_standard_output_generation(capsys):
    """
    Test that lshw (without arguments) produces human-readable output.
    This checks that Hardware objects are correctly processed by the pretty printer.
    """
    # Mock argv (no arguments)
    test_argv = []

    with patch('lshw.__main__.HardwareClass') as mock_hardware_class:
        # User requests full system info by default
        mock_instance = MagicMock()

        # Create a dummy Hardware object
        # Note: pretty() looks for keys and values. Hardware object is not a dict.
        hw = Hardware(id='test-pc', product='Test Computer', description='A test computer')

        # format_data returns a list of Hardware objects
        mock_instance.format_data.return_value = [hw]

        # Setup the factory
        mock_hardware_class.factory.return_value = MagicMock(return_value=mock_instance)

        # Run main
        exit_code = main(test_argv)

        # Assert exit code 0
        assert exit_code == 0

        # Capture stdout
        captured = capsys.readouterr()

        # The output should contain the product name if printing works
        assert 'Test Computer' in captured.out
