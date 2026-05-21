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
from .hardware_class import HardwareClass, wmi

logger = logging.getLogger(__name__)


@HardwareClass.register('Power', parent='BaseBoard')
class Power(HardwareClass):
    """
    Gets power supply and battery information using WMI
    """

    def __init__(self):
        super().__init__()

        self.hardware = Hardware(
            id=self.__ERROR__,
            class_='power',
            claimed=True,
            handle='',
            description='Power Supply / Battery',
            product=self.__ERROR__,
            vendor=self.__ERROR__,
            physid='',
            serial='',
        )
        self.hardware.capacity = 0
        self.hardware.configuration = {
            'chemistry': '',
        }

        self.properties_to_get = [
            'DeviceID',
            'Description',
            'Name',
            'Caption',
            'Manufacturer',
            'SerialNumber',
            'DesignCapacity',
            'Chemistry',
        ]

        self._update_properties_to_return()
        self._power_id = 0

    def get_hardware(self):
        # Clear hardware_set to avoid duplicates if run multiple times
        self.hardware_set = []
        self.hardware_set_to_return = []

        # Query Win32_Battery
        try:
            self._validate_entity('Win32_Battery')
            self.execute_wql_query('SELECT * FROM Win32_Battery')
        except (wmi.x_wmi, AttributeError, ValueError) as e:
            logger.debug(f'Could not query Win32_Battery: {e}')

        # Query Win32_PortableBattery
        try:
            self._validate_entity('Win32_PortableBattery')
            self.execute_wql_query('SELECT * FROM Win32_PortableBattery')
        except (wmi.x_wmi, AttributeError, ValueError) as e:
            logger.debug(f'Could not query Win32_PortableBattery: {e}')

        # Query Win32_UninterruptiblePowerSupply
        try:
            self._validate_entity('Win32_UninterruptiblePowerSupply')
            self.execute_wql_query('SELECT * FROM Win32_UninterruptiblePowerSupply')
        except (wmi.x_wmi, AttributeError, ValueError) as e:
            logger.debug(f'Could not query Win32_UninterruptiblePowerSupply: {e}')

        self.check_values()

    def _populate_hardware(self, item_ret: Hardware, hw_item: dict) -> Hardware:
        item_ret.id = f'power:{self._power_id}'
        self._power_id += 1

        desc = hw_item.get('Description')
        if not desc or desc == self.__DESC__:
            desc = hw_item.get('Caption', 'Power Supply / Battery')
        item_ret.description = desc

        prod = hw_item.get('Name')
        if not prod or prod == self.__DESC__:
            prod = hw_item.get('Caption', self.__ERROR__)
        item_ret.product = prod

        item_ret.vendor = hw_item.get('Manufacturer', self.__ERROR__)

        serial = hw_item.get('SerialNumber')
        if serial and serial != self.__DESC__:
            item_ret.serial = str(serial).strip()
        else:
            item_ret.serial = ''

        capacity = hw_item.get('DesignCapacity')
        if capacity and capacity != self.__DESC__:
            try:
                item_ret.capacity = int(capacity)
            except (ValueError, TypeError):
                item_ret.capacity = 0

        chem = hw_item.get('Chemistry')
        if chem and chem != self.__DESC__:
            item_ret.configuration['chemistry'] = str(chem).strip()

        return item_ret
