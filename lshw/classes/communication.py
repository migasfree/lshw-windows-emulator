# Copyright (c) 2026 Jose Antonio Chavarría <jachavar@gmail.com>
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

import logging

from .hardware import Hardware
from .hardware_class import HardwareClass

logger = logging.getLogger(__name__)


@HardwareClass.register('Communication', parent='Pci')
class Communication(HardwareClass):
    """
    Gets communication (serial ports and modems) information using WMI
    """

    def __init__(self):
        super().__init__()

        self.hardware = Hardware(
            id=self.__ERROR__,
            class_='communication',
            claimed=True,
            handle='',
            description='Communication device',
            product=self.__ERROR__,
            vendor=self.__ERROR__,
            physid='',
            serial='',
        )
        self.hardware.logicalname = ''
        self.hardware.clock = 0

        self.properties_to_get = [
            'DeviceID',
            'Description',
            'Name',
            'ProviderType',
            'MaxBaudRate',
            'Caption',
            'AttachedTo',
            'Manufacturer',
            'ProviderName',
        ]

        self._update_properties_to_return()
        self._comm_id = 0

    def get_hardware(self):
        # Clear hardware_set to avoid duplicates if run multiple times
        self.hardware_set = []
        self.hardware_set_to_return = []

        # Query Win32_SerialPort
        try:
            self._validate_entity('Win32_SerialPort')
            self.execute_wql_query('SELECT * FROM Win32_SerialPort')
        except Exception as e:
            logger.debug(f'Could not query Win32_SerialPort: {e}')

        # Query Win32_POTSModem
        try:
            self._validate_entity('Win32_POTSModem')
            self.execute_wql_query('SELECT * FROM Win32_POTSModem')
        except Exception as e:
            logger.debug(f'Could not query Win32_POTSModem: {e}')

        self.check_values()

    def _populate_hardware(self, item_ret: Hardware, hw_item: dict) -> Hardware:
        item_ret.id = f'communication:{self._comm_id}'
        self._comm_id += 1

        desc = hw_item.get('Description')
        if not desc or desc == self.__DESC__:
            desc = hw_item.get('Caption', 'Communication device')
        item_ret.description = desc

        item_ret.product = hw_item.get('Name', self.__ERROR__)

        # Vendor extraction
        vendor = hw_item.get('Manufacturer')
        if not vendor or vendor == self.__DESC__:
            vendor = hw_item.get('ProviderName')
        if not vendor or vendor == self.__DESC__:
            vendor = hw_item.get('ProviderType', self.__ERROR__)
        item_ret.vendor = vendor

        # Logical name (Attached COM port or DeviceID)
        attached_to = hw_item.get('AttachedTo')
        if attached_to and attached_to != self.__DESC__:
            item_ret.logicalname = str(attached_to).strip()
        else:
            item_ret.logicalname = str(hw_item.get('DeviceID', self.__ERROR__)).strip()

        baud = hw_item.get('MaxBaudRate')
        if baud and baud != self.__DESC__:
            try:
                item_ret.clock = int(baud)
            except (ValueError, TypeError):
                item_ret.clock = 0

        return item_ret
