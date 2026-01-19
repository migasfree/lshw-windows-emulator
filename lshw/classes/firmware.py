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

from .hardware_class import HardwareClass


@HardwareClass.register('Firmware')
class Firmware(HardwareClass):
    """
    Gets Firmware/BIOS information using WMI
    """

    def __init__(self):
        super().__init__()

        self.wmi_method = 'Win32_bios'

        self.formatted_data = {
            'id': 'firmware',
            'class': 'memory',
            'claimed': True,
            'description': 'BIOS',
            'vendor': self.__ERROR__,
            'physid': '',
            'version': self.__ERROR__,
            'date': self.__ERROR__,
            'serial': self.__ERROR__,
            'units': '',
            'size': 0,
            'capacity': 0,
        }

        self.properties_to_get = ['Manufacturer', 'BIOSVersion', 'ReleaseDate', 'SerialNumber']

        self._update_properties_to_return()

    def format_data(self, children=False):
        self.get_hardware()

        for hw_item in self.hardware_set_to_return:
            self.formatted_data['vendor'] = hw_item.get('Manufacturer', self.__ERROR__)
            self.formatted_data['date'] = hw_item.get('ReleaseDate', self.__ERROR__)
            self.formatted_data['serial'] = hw_item.get('SerialNumber', self.__ERROR__)
            if 'BIOSVersion' in hw_item:
                self.formatted_data['version'] = hw_item['BIOSVersion'][0]

        return self.formatted_data
