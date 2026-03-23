from cx_Freeze import Executable, setup

# Import version from the package
from lshw import __version__

# Dependencies are automatically detected, but they might need fine tuning.
build_exe_options = {
    'packages': ['os', 'lshw', 'psutil', 'wmi', 'win32com'],
    'excludes': ['tkinter', 'unittest', 'pydoc'],
}

# bdist_msi options for the Windows Installer
bdist_msi_options = {
    'add_to_path': True,
    'initial_target_dir': r'[ProgramFilesFolder]\lshw',
    # cx_Freeze automatically generates an UpgradeCode based on the project name.
}

# base="Console" is used for CLI applications
base = 'Console'

setup(
    name='lshw-windows-emulator',
    version=__version__,
    description='lshw Windows Emulator',
    options={
        'build_exe': build_exe_options,
        'bdist_msi': bdist_msi_options,
    },
    executables=[
        Executable(
            'lshw/__main__.py',
            target_name='lshw.exe',
            base=base,
        )
    ],
)
