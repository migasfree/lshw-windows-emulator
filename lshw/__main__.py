# -*- coding: UTF-8 -*-

# Copyright (c) 2021-2022 Jose Antonio Chavarría <jachavar@gmail.com>
# Copyright (c) 2011-2021 Alfonso Gómez Sánchez <agomez@zaragoza.es>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

__author__ = [
    'Jose Antonio Chavarría <jachavar@gmail.com>',
    'Alfonso Gómez Sánchez <agomez@zaragoza.es>'
]
__license__ = 'GPLv3'

import sys
import argparse
import json

from .classes import HardwareClass

PROGRAM = 'lshw'
ALL_OK = 0

AVAILABLE_CLASSES = {
    "system": ['ComputerSystem', 1],
    "baseboard": ['BaseBoard', 2],
    "bios": ['Firmware', 2],
    "processor": ['Processor', 3],
    "memory": ['PhysicalMemory', 4],
    "pci": ['BusPci', 5],
    "ide": ['Ide', 6],
    "disk": ['PhysicalDisk', 7],
    "partition": ['PartitionDisk', 8],
    "volume": ['LogicalDisk', 9],
    "usb": ['Usb', 10],
    "usbdevices": ['UsbDevice', 11],
    "cdrom": ['CdRom', 12],
    "video": ['GraphicCard', 13],
    "network": ['NetworkCard', 14],
    "sound": ['SoundDevice', 15]
}


def _exit_manager(exit_code, exit_element=''):
    """
    Exit management
    Print exit text

    exit_code: Number exit code
    exit_element: Element afected by exit code
    """

    if exit_code >= 1 and exit_code <= 16:
        _exit_message = 'there was an error getting "[element]" information'
        if exit_code == 16:
            _exit_message = 'There was a critical error getting hardware information'

        _exit_text = '[err #{}] {}'.format(
            exit_code,
            _exit_message.replace('[element]', exit_element)
        )
        print('\n\n')
        sys.stderr.write(_exit_text)
        return exit_code

    return exit_code


def _usage_examples():
    print('\n' + 'Examples:')

    print('\n  ' + 'Output in JSON format:')
    print(f'\t{PROGRAM} -j')
    print(f'\t{PROGRAM} --json')

    print('\n  ' + 'Print a specific hardware class:')
    print(f'\t{PROGRAM} --c memory')
    print(f'\t{PROGRAM} --class-hw memory')


def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog=PROGRAM,
        description='Hardware Lister Windows Emulator',
    )

    parser.add_argument(
        '--json', '-j',
        action='store_true',
        help='output in JSON format (indented)'
    )

    parser.add_argument(
        '--class-hw', '-c',
        action='store',
        help='print a specific hardware class (write "-c list" to get available classes)'
    )

    return parser.parse_args()


def pretty(d, indent=0):
    if isinstance(d, list):
        for i in d:
            pretty(i, indent + 1)

    if isinstance(d, dict):
        for key, value in d.items():
            if isinstance(value, dict) or isinstance(value, list):
                pretty(value, indent + 1)
            else:
                print('\t' * (indent + 1) + str(key) + ': ' + str(value))


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_args(argv)

    if args.class_hw:
        _piece = args.class_hw.strip()
        _class = ''
        if _piece == 'list':
            _help_msg = "Pieces of hardware to choice:\n"
            for x, y in AVAILABLE_CLASSES.items():
                _help_msg += f'\t{x}\n'

            print(_help_msg)
            return ALL_OK

        for x, y in AVAILABLE_CLASSES.items():
            if _piece == x:
                _class = y[0]
                try:
                    hw_class = HardwareClass.factory(_class)()
                    formatted_data = hw_class.format_data(children=False)
                except:
                    return _exit_manager(y[1], _class)

        if not _class:
            # parser.print_help()
            _usage_examples()
            return -1  # FIXME
    else:
        # get full computer information
        try:
            hw_class = HardwareClass.factory('ComputerSystem')()
            formatted_data = hw_class.format_data(children=True)
        except:
            return _exit_manager(16, 'system')

    if args.json:
        print(json.dumps(formatted_data, indent=2))
    else:
        pretty(formatted_data)

    return ALL_OK


if __name__ == '__main__':
    sys.exit(main() or ALL_OK)
