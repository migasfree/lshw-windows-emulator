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


@HardwareClass.register('CdRom')
class CdRom(HardwareClass):
    """
    Gets CDROM/DVDROM  units information using WMI
    """

    def __init__(self, dev_id=''):
        HardwareClass.__init__(self)

        self.dev_id = dev_id

        self.formatted_data = {
            "id": "cdrom",
            "class": "disk",
            "claimed": True,
            "handle": "",
            "description": self.__ERROR__,
            "product": self.__ERROR__,
            "vendor": self.__ERROR__,
            "physid": "",
            "businfo": "",
            "logicalname": self.__ERROR__,
            "DeviceID": self.__ERROR__,
            "PNPDeviceID": self.__ERROR__,
            "dev": "",
            "version": "",
            "configuration": {
                "ansiversion": "",
                "status": self.__ERROR__
            },
            "capabilities": {
                "removable": "",
                "audio": "",
                "cd-r": "",
                "cd-rw": "",
                "dvd": "",
                "dvd-r": "",
                "dvd-ram": ""
            }
        }

        self.properties_to_get = [
            "DeviceID",
            "PNPDeviceID",
            "Manufacturer",
            "Name",
            "Caption",
            "MediaType",
            "SCSIBus",
            "SCSILogicalUnit",
            "SCSIPort",
            "Description",
            "MediaLoaded",
            "Drive"
        ]

        self._update_properties_to_return()

    def get_hardware(self):
        """
        Get Hardware set
        If dev_id exists get hardware for DeviceID
        """

        # Win32_CDROMDrive
        if self.dev_id == '':
            for element in self.wmi_system.Win32_cdromdrive(
                self.properties_to_get
            ):
                self.hardware_set.append(element)
        else:
            wql = 'SELECT {} FROM Win32_cdromdrive WHERE PNPDeviceID LIKE "%{}%"'.format(
                ','.join(self.properties_to_get),
                self.dev_id
            )
            for element in self.wmi_system.query(wql):
                self.hardware_set.append(element)

        self.check_values()

    def format_data(self, children=False):
        self.get_hardware()

        ret = []
        for hw_item in self.hardware_set_to_return:
            media_loaded = 'no disc'
            if 'MediaLoaded' in hw_item and hw_item['MediaLoaded'] is True:
                media_loaded = 'loaded disc'

            item_ret = deepcopy(self.formatted_data)
            item_ret['description'] = hw_item.get('Description', self.__ERROR__)
            item_ret['product'] = hw_item.get('Name', self.__ERROR__)
            item_ret['vendor'] = hw_item.get('Manufacturer', self.__ERROR__)
            item_ret['logicalname'] = hw_item.get('Drive', self.__ERROR__)
            item_ret['DeviceID'] = hw_item.get('DeviceID', self.__ERROR__)
            item_ret['PNPDeviceID'] = hw_item.get('PNPDeviceID', self.__ERROR__)
            item_ret['configuration']['status'] = media_loaded

            ret.append(item_ret)

        return ret
