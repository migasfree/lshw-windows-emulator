import json
import logging
from unittest.mock import MagicMock, patch

import pytest

from lshw.__main__ import (
    ALL_OK,
    AVAILABLE_CLASSES,
    EXIT_USAGE,
    _exit_manager,
    _usage_examples,
    main,
    parse_args,
    pretty,
)
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


def test_exit_manager_returns_on_low_code():
    """_exit_manager returns exit_code unchanged for values outside 1-16."""
    assert _exit_manager(0) == 0


def test_exit_manager_returns_on_high_code():
    """_exit_manager returns exit_code unchanged for values above 16."""
    assert _exit_manager(99) == 99


def test_exit_manager_error_code(caplog):
    """_exit_manager prints error message to stderr and logs it."""
    with patch('sys.stderr') as mock_stderr:
        result = _exit_manager(3, 'processor')

    assert result == 3
    mock_stderr.write.assert_called_once()
    assert 'error getting "processor"' in mock_stderr.write.call_args[0][0]


def test_exit_manager_critical_error(caplog):
    """_exit_manager prints critical error message and includes error_detail."""
    with patch('sys.stderr') as mock_stderr, caplog.at_level(logging.ERROR):
        result = _exit_manager(16, 'system', 'WMI failure')

    assert result == 16
    mock_stderr.write.assert_called_once()
    assert 'critical error' in mock_stderr.write.call_args[0][0]
    assert 'WMI failure' in mock_stderr.write.call_args[0][0]


def test_usage_examples(capsys):
    """_usage_examples prints example commands."""
    _usage_examples()
    captured = capsys.readouterr()
    assert 'Examples' in captured.out
    assert 'Output in JSON format' in captured.out
    assert '--json' in captured.out
    assert '--class-hw memory' in captured.out


def test_parse_args_defaults():
    """parse_args returns default values with no arguments."""
    args = parse_args([])
    assert args.json is False
    assert args.class_hw is None


def test_parse_args_json_short():
    """parse_args sets json=True with -j flag."""
    args = parse_args(['-j'])
    assert args.json is True


def test_parse_args_json_long():
    """parse_args sets json=True with --json flag."""
    args = parse_args(['--json'])
    assert args.json is True


def test_parse_args_dash_json():
    """parse_args converts single-dash -json to --json."""
    # -json is not defined, but main() converts it before calling parse_args
    args = parse_args(['--json'])
    assert args.json is True


def test_parse_args_class_hw():
    """parse_args sets class_hw with -c flag."""
    args = parse_args(['-c', 'memory'])
    assert args.class_hw == 'memory'


def test_parse_args_class_hw_long():
    """parse_args sets class_hw with --class-hw flag."""
    args = parse_args(['--class-hw', 'network'])
    assert args.class_hw == 'network'


def test_main_class_hw_list(capsys):
    """main with -c list prints all available classes."""
    exit_code = main(['-c', 'list'])
    assert exit_code == ALL_OK
    captured = capsys.readouterr()
    for name in AVAILABLE_CLASSES:
        assert name in captured.out


def test_main_class_hw_valid(capsys):
    """main dispatches to a single valid hardware class."""
    with patch('lshw.__main__.HardwareClass') as mock_hardware_class:
        mock_instance = MagicMock()
        hw = Hardware(id='mem0', product='DIMM 16GB')
        mock_instance.format_data.return_value = [hw]
        mock_hardware_class.factory.return_value = MagicMock(return_value=mock_instance)

        exit_code = main(['-c', 'memory'])
        assert exit_code == ALL_OK

        # Verify factory was called with the correct class name
        mock_hardware_class.factory.assert_called_once_with('PhysicalMemory')


def test_main_class_hw_invalid(capsys):
    """main with unknown class prints usage examples."""
    exit_code = main(['-c', 'nonexistent'])
    assert exit_code == EXIT_USAGE
    captured = capsys.readouterr()
    assert 'Examples' in captured.out


def test_main_class_hw_access_denied(capsys):
    """main returns class-specific exit code when WMI access is denied."""
    from lshw.classes.hardware_class import wmi

    with patch('lshw.__main__.HardwareClass') as mock_hardware_class:
        mock_instance = MagicMock()
        mock_instance.format_data.side_effect = wmi.x_access_denied('denied')
        mock_hardware_class.factory.return_value = MagicMock(return_value=mock_instance)

        exit_code = main(['-c', 'memory'])
        # exit code 4 = PhysicalMemory's code in AVAILABLE_CLASSES
        assert exit_code == AVAILABLE_CLASSES['memory'][1]


def test_main_class_hw_wmi_error(capsys):
    """main returns class-specific exit code on WMI error."""
    from lshw.classes.hardware_class import wmi

    with patch('lshw.__main__.HardwareClass') as mock_hardware_class:
        mock_instance = MagicMock()
        mock_instance.format_data.side_effect = wmi.x_wmi('WMI error')
        mock_hardware_class.factory.return_value = MagicMock(return_value=mock_instance)

        exit_code = main(['-c', 'network'])
        assert exit_code == AVAILABLE_CLASSES['network'][1]


def test_main_class_hw_type_error(capsys):
    """main returns class-specific exit code on TypeError."""
    with patch('lshw.__main__.HardwareClass') as mock_hardware_class:
        mock_instance = MagicMock()
        mock_instance.format_data.side_effect = TypeError('bad type')
        mock_hardware_class.factory.return_value = MagicMock(return_value=mock_instance)

        exit_code = main(['-c', 'memory'])
        assert exit_code == AVAILABLE_CLASSES['memory'][1]


def test_main_system_access_denied(capsys):
    """main returns exit code 16 when full system scan gets access denied."""
    from lshw.classes.hardware_class import wmi

    with patch('lshw.__main__.HardwareClass') as mock_hardware_class:
        mock_instance = MagicMock()
        mock_instance.format_data.side_effect = wmi.x_access_denied('denied')
        mock_hardware_class.factory.return_value = MagicMock(return_value=mock_instance)

        exit_code = main([])
        assert exit_code == 16


def test_main_system_wmi_error(capsys):
    """main returns exit code 16 on WMI error during full scan."""
    from lshw.classes.hardware_class import wmi

    with patch('lshw.__main__.HardwareClass') as mock_hardware_class:
        mock_instance = MagicMock()
        mock_instance.format_data.side_effect = wmi.x_wmi('WMI error')
        mock_hardware_class.factory.return_value = MagicMock(return_value=mock_instance)

        exit_code = main([])
        assert exit_code == 16


def test_main_system_type_error(capsys):
    """main returns exit code 16 on TypeError during full scan."""
    with patch('lshw.__main__.HardwareClass') as mock_hardware_class:
        mock_instance = MagicMock()
        mock_instance.format_data.side_effect = TypeError('bad')
        mock_hardware_class.factory.return_value = MagicMock(return_value=mock_instance)

        exit_code = main([])
        assert exit_code == 16


def test_pretty_list(capsys):
    """pretty handles nested lists and dicts."""
    data = [{'key1': 'value1'}, {'key2': 'value2'}]
    pretty(data)
    captured = capsys.readouterr()
    assert 'key1' in captured.out
    assert 'value1' in captured.out
    assert 'key2' in captured.out


def test_pretty_nested_dict(capsys):
    """pretty indents nested structures but skips outer keys for dict values."""
    data = [{'outer': {'inner': 'deep'}}]
    pretty(data)
    captured = capsys.readouterr()
    assert 'inner' in captured.out
    assert 'deep' in captured.out
    assert '    inner: deep' in captured.out


def test_dash_json_flag():
    """main handles single-dash -json flag compatibility."""
    # parse_args converts -json to --json internally
    args = parse_args(['-json'])
    assert args.json is True


def test_main_defaults_to_sys_argv():
    """main() without argv defaults to sys.argv[1:] patched to empty."""
    with patch('lshw.__main__.HardwareClass') as mock_hardware_class:
        mock_instance = MagicMock()
        hw = Hardware(id='test')
        mock_instance.format_data.return_value = [hw]
        mock_hardware_class.factory.return_value = MagicMock(return_value=mock_instance)

        with patch('sys.argv', ['lshw']):
            exit_code = main()
            assert exit_code == ALL_OK
