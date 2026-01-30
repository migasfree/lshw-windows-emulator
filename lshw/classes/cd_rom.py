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


@HardwareClass.register('CdRom', parent='Ide')
class CdRom(HardwareClass):
    """
    Gets CDROM/DVDROM information using WMI
    """

    def __init__(self, dev_id=''):
        super().__init__()

        self.dev_id = dev_id

        self.hardware = Hardware(
            id='cdrom',
            class_='disk',
            claimed=True,
            handle='',
            description=self.__ERROR__,
            product=self.__ERROR__,
            vendor=self.__ERROR__,
            physid='',
            serial='',
        )
        self.hardware.businfo = ''
        self.hardware.logicalname = self.__ERROR__
        self.hardware.deviceid = self.__ERROR__
        self.hardware.pnpdeviceid = self.__ERROR__
        self.hardware.dev = ''
        self.hardware.version = ''
        self.hardware.configuration = {'ansiversion': '', 'status': self.__ERROR__}
        self.hardware.capabilities = {
            'removable': '',
            'audio': '',
            'cd-r': '',
            'cd-rw': '',
            'dvd': '',
            'dvd-r': '',
            'dvd-ram': '',
        }

        self.properties_to_get = [
            'DeviceID',
            'PNPDeviceID',
            'Manufacturer',
            'Name',
            'Caption',
            'MediaType',
            'SCSIBus',
            'SCSILogicalUnit',
            'SCSIPort',
            'Description',
            'MediaLoaded',
            'Drive',
        ]

        self._update_properties_to_return()

    def get_hardware(self):
        """
        Get Hardware set
        If dev_id exists get hardware for DeviceID
        """

        # Win32_CDROMDrive
        if self.dev_id == '':
            for element in self.wmi_system.Win32_cdromdrive(self.properties_to_get):
                self.hardware_set.append(element)
        else:
            wql = self.build_wql_select('Win32_cdromdrive', f'PNPDeviceID LIKE "%{self.dev_id}%"')
            self.execute_wql_query(wql)

        self.check_values()

    def format_data(self, children=False):
        self.get_hardware()

        ret = []
        for hw_item in self.hardware_set_to_return:
            media_loaded = 'no disc'
            if 'MediaLoaded' in hw_item and hw_item['MediaLoaded'] is True:
                media_loaded = 'loaded disc'

            item_ret = Hardware(
                id='cdrom',
                class_='disk',
                claimed=True,
                handle='',
                description=hw_item.get('Description', self.__ERROR__),
                product=hw_item.get('Name', self.__ERROR__),
                vendor=hw_item.get('Manufacturer', self.__ERROR__),
                physid='',
                serial='',
            )
            item_ret.businfo = ''
            item_ret.logicalname = hw_item.get('Drive', self.__ERROR__)
            item_ret.deviceid = hw_item.get('DeviceID', self.__ERROR__)
            item_ret.pnpdeviceid = hw_item.get('PNPDeviceID', self.__ERROR__)
            item_ret.dev = ''
            item_ret.version = ''
            item_ret.configuration = {'ansiversion': '', 'status': media_loaded}
            item_ret.capabilities = {
                'removable': '',
                'audio': '',
                'cd-r': '',
                'cd-rw': '',
                'dvd': '',
                'dvd-r': '',
                'dvd-ram': '',
            }

            ret.append(item_ret)

        return ret
