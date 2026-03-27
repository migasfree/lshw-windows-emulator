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


@HardwareClass.register('BaseBoard', parent='ComputerSystem')
class BaseBoard(HardwareClass):
    """
    Gets Base Board information using WMI
    """

    def __init__(self):
        super().__init__()

        self.wmi_method = 'Win32_baseboard'

        self.hardware = Hardware(
            id='core',
            class_='bus',
            claimed=True,
            handle='',
            description='Motherboard',
            product=self.__ERROR__,
            vendor=self.__ERROR__,
            physid='0',
            serial=self.__ERROR__,
        )

        self.properties_to_get = ['Model', 'SerialNumber', 'Manufacturer', 'Product']

        self._update_properties_to_return()

    def _populate_hardware(self, item_ret: Hardware, hw_item: dict) -> Hardware:
        item_ret.product = hw_item.get('Product', self.__ERROR__)
        item_ret.vendor = hw_item.get('Manufacturer', self.__ERROR__)
        item_ret.serial = hw_item.get('SerialNumber', self.__ERROR__)
        return item_ret
