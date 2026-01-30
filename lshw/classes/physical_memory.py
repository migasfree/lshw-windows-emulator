# Copyright (c) 2021-2026 Jose Antonio Chavarría <jachavar@gmail.com>
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

__author__ = ['Jose Antonio Chavarría <jachavar@gmail.com>', 'Alfonso Gómez Sánchez <agomez@zaragoza.es>']
__license__ = 'GPLv3'

import logging

from .hardware import Hardware
from .hardware_class import HardwareClass

logger = logging.getLogger(__name__)


@HardwareClass.register('PhysicalMemory', parent='BaseBoard')
class PhysicalMemory(HardwareClass):
    """
    Gets physical memory information using WMI
    """

    def __init__(self):
        super().__init__()

        self.wmi_method = 'Win32_physicalMemory'

        self.hardware = Hardware(
            id='memory:0',
            class_='memory',
            claimed=True,
            handle='',
            description='System Memory',
            physid='',
        )
        self.hardware.slot = ''

        self.properties_to_get = [
            'Tag',
            'DeviceLocator',
            'Capacity',
            'Speed',
            'MemoryType',
            'DataWidth',
        ]

        self._update_properties_to_return()

    def format_data(self, children=False):
        self.get_hardware()

        for hw_item in self.hardware_set_to_return:
            bank = Hardware(
                id=self.__ERROR__,
                class_='memory',
                claimed=True,
                handle='',
                description=self.__ERROR__,
                product=self.__ERROR__,
                vendor='',
                physid='',
                serial='',
            )
            bank.slot = self.__ERROR__
            bank.units = 'bytes'
            bank.size = self.__ERROR__
            bank.width = self.__ERROR__
            bank.clock = self.__ERROR__

            if 'Tag' in hw_item:
                bank.id = f'bank:{hw_item["Tag"][-1]}'

            bank.description = hw_item.get('Tag', self.__ERROR__)
            bank.product = hw_item.get('MemoryType', self.__ERROR__)
            bank.slot = hw_item.get('DeviceLocator', self.__ERROR__)
            bank.size = hw_item.get('Capacity', 0)
            bank.width = hw_item.get('DataWidth', 0)
            bank.clock = hw_item.get('Speed', 0)

            self.hardware.children.append(bank)

        if not self.hardware_set_to_return:
            try:
                for item in self.wmi_system.Win32_ComputerSystem(['TotalPhysicalMemory']):
                    bank = Hardware(
                        id='bank:0',
                        class_='memory',
                        claimed=True,
                        handle='',
                        description='System Memory',
                        product='System Memory',
                        vendor='',
                        physid='',
                        serial='',
                    )
                    bank.slot = 'System Board'
                    bank.units = 'bytes'
                    bank.size = int(item.TotalPhysicalMemory)
                    bank.width = 64
                    bank.clock = 0

                    self.hardware.children.append(bank)
            except Exception as e:
                logger.error(f'Error getting memory from Win32_ComputerSystem: {e}')

        return [self.hardware]
