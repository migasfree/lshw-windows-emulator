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

from .firmware import Firmware
from .hardware_class import HardwareClass
from .pci import Pci
from .physical_memory import PhysicalMemory
from .processor import Processor


@HardwareClass.register('BaseBoard')
class BaseBoard(HardwareClass):
    """
    Gets Base Board information using WMI
    """

    def __init__(self):
        super().__init__()

        self.wmi_method = 'Win32_baseboard'

        self.formatted_data = {
            'id': 'core',
            'class': 'bus',
            'claimed': True,
            'handle': '',
            'description': 'Motherboard',
            'product': self.__ERROR__,
            'vendor': self.__ERROR__,
            'physid': '0',
            'serial': self.__ERROR__,
            'children': [],
        }

        self.properties_to_get = ['Model', 'SerialNumber', 'Manufacturer', 'Product']

        self._update_properties_to_return()

    def format_data(self, children=False):
        self.get_hardware()

        for hw_item in self.hardware_set_to_return:
            self.formatted_data['product'] = hw_item.get('Product', self.__ERROR__)
            self.formatted_data['vendor'] = hw_item.get('Manufacturer', self.__ERROR__)
            self.formatted_data['serial'] = hw_item.get('SerialNumber', self.__ERROR__)

        if children:
            self.formatted_data['children'] = [
                Firmware().format_data(),
                PhysicalMemory().format_data(),
                Pci().format_data(children=True),
            ]
            for item in Processor().format_data():
                self.formatted_data['children'].append(item)

        return self.formatted_data
