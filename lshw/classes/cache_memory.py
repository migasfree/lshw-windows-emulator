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

__author__ = ['Jose Antonio Chavarría <jachavar@gmail.com>', 'Alfonso Gómez Sánchez <agomez@zaragoza.es>']
__license__ = 'GPLv3'

from .hardware import Hardware
from .hardware_class import HardwareClass


@HardwareClass.register('CacheMemory', parent='Processor')
class CacheMemory(HardwareClass):
    """
    Gets cache memory information (L1, L2, L3) using WMI
    """

    def __init__(self):
        super().__init__()

        self.wmi_method = 'Win32_CacheMemory'

        self.hardware = Hardware(
            id=self.__ERROR__,
            class_='memory',
            claimed=True,
            handle='',
            description=self.__ERROR__,
            product=self.__ERROR__,
            vendor=self.__ERROR__,
            physid='',
            serial='',
        )
        self.hardware.slot = self.__ERROR__
        self.hardware.size = 0

        self.properties_to_get = [
            'DeviceID',
            'InstalledSize',
            'Level',
            'Purpose',
            'Status',
        ]

        self._update_properties_to_return()
        self._cache_id = 0

    def _populate_hardware(self, item_ret: Hardware, hw_item: dict) -> Hardware:
        item_ret.id = f'cache:{self._cache_id}'
        self._cache_id += 1

        size_kb = hw_item.get('InstalledSize', 0)
        try:
            item_ret.size = int(size_kb) * 1024
        except (ValueError, TypeError):
            item_ret.size = 0

        level = hw_item.get('Level')
        level_map = {3: 'L1', 4: 'L2', 5: 'L3'}
        try:
            level_val = int(level)
            level_str = level_map.get(level_val, f'L{level_val - 2}' if level_val > 2 else 'Unknown')
        except (ValueError, TypeError):
            level_str = 'Unknown'

        item_ret.description = f'{level_str} cache' if level_str != 'Unknown' else 'Cache Memory'
        item_ret.product = hw_item.get('Purpose') or item_ret.description
        item_ret.slot = hw_item.get('DeviceID', self.__ERROR__)
        item_ret.vendor = ''

        return item_ret
