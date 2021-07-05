# -*- coding: UTF-8 -*-

# Copyright (c) 2021 Jose Antonio Chavarría <jachavar@gmail.com>
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

from copy import deepcopy

from .hardware_class import HardwareClass


@HardwareClass.register('PhysicalMemory')
class PhysicalMemory(HardwareClass):
    """
    Gets physical memory information using WMI
    """

    def __init__(self):
        super().__init__()

        self.wmi_method = 'Win32_physicalMemory'

        self.formatted_data = {
            'id': 'memory:0',
            'class': 'memory',
            'claimed': True,
            'handle': '',
            'description': 'System Memory',
            'physid': '',
            'slot': '',
            'children': []
        }

        self.formatted_data_default = {
            'id': self.__ERROR__,
            'class': 'memory',
            'claimed': True,
            'handle': '',
            'description': self.__ERROR__,
            'product': self.__ERROR__,
            'vendor': '',
            'physid': '',
            'serial': '',
            'slot': self.__ERROR__,
            'units': 'bytes',
            'size': self.__ERROR__,
            'width': self.__ERROR__,
            'clock': self.__ERROR__
        }

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

        ret = []
        for hw_item in self.hardware_set_to_return:
            item_ret = deepcopy(self.formatted_data_default)

            if 'Tag' in hw_item:
                item_ret['id'] = 'bank:{}'.format(hw_item['Tag'][-1])

            item_ret['description'] = hw_item.get('Tag', self.__ERROR__)
            item_ret['product'] = hw_item.get('MemoryType', self.__ERROR__)
            item_ret['slot'] = hw_item.get('DeviceLocator', self.__ERROR__)
            item_ret['size'] = hw_item.get('Capacity', 0)
            item_ret['width'] = hw_item.get('DataWidth', 0)
            item_ret['clock'] = hw_item.get('Speed', 0)

            ret.append(item_ret)

        self.formatted_data['children'] = ret

        return self.formatted_data
