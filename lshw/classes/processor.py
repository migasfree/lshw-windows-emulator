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

from .hardware import Hardware
from .hardware_class import HardwareClass


@HardwareClass.register('Processor', parent='BaseBoard')
class Processor(HardwareClass):
    """
    Gets processor/CPU information using WMI
    """

    def __init__(self):
        super().__init__()

        self.wmi_method = 'Win32_processor'

        self.hardware = Hardware(
            id=self.__ERROR__,
            class_='processor',
            claimed=True,
            handle='',
            description=self.__ERROR__,
            product=self.__ERROR__,
            vendor=self.__ERROR__,
            physid='',
            serial='',
        )
        self.hardware.businfo = 'cpu@'
        self.hardware.version = ''
        self.hardware.slot = self.__ERROR__
        self.hardware.units = 'Hz'
        self.hardware.size = 0
        self.hardware.width = self.__ERROR__
        self.hardware.clock = self.__ERROR__

        self.properties_to_get = [
            'Manufacturer',
            'Name',
            'Description',
            'SocketDesignation',
            'DataWidth',
            'MaxClockSpeed',
        ]

        self._update_properties_to_return()
        self._cpu_id = 0

    def _populate_hardware(self, item_ret: Hardware, hw_item: dict) -> Hardware:
        item_ret.id = f'cpu:{self._cpu_id}'
        self._cpu_id += 1

        item_ret.description = hw_item.get('Description', self.__ERROR__)
        item_ret.product = hw_item.get('Name', self.__ERROR__)
        item_ret.vendor = hw_item.get('Manufacturer', self.__ERROR__)
        item_ret.slot = hw_item.get('SocketDesignation', self.__ERROR__)
        item_ret.width = hw_item.get('DataWidth', self.__ERROR__)
        item_ret.clock = hw_item.get('MaxClockSpeed', self.__ERROR__)

        return item_ret
