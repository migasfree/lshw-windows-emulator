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
from .partition_disk import PartitionDisk


@HardwareClass.register('PhysicalDisk')
class PhysicalDisk(HardwareClass):
    """
    Gets physical disk information using WMI
    """

    def __init__(self, dev_id=''):
        HardwareClass.__init__(self)

        self.dev_id = dev_id

        self.formatted_data = {
            "id": "disk",
            "class": "disk",
            "claimed": True,
            "handle": "",
            "description": self.__ERROR__,
            "product": self.__ERROR__,
            "vendor": self.__ERROR__,
            "physid": "",
            "deviceid": self.__ERROR__,
            "pnpdeviceid": self.__ERROR__,
            "businfo": self.__ERROR__,
            "logicalname": "",
            "dev": "",
            "version": "",
            "serial": "",
            "units": "bytes",
            "size": 0,
            "configuration": {
                "ansiversion": "",
                "signature": ""
            },
            "capabilities": {
                "partitioned": "",
                "partitioned:dos": ""
            },
            "children": []
        }

        self.properties_to_get = [
            "Caption",
            "Description",
            "DeviceID",
            "Index",
            "Manufacturer",
            "PNPDeviceID",
            "Size",
        ]

        self._update_properties_to_return()

    def get_hardware(self):
        """
        Get Hardware set
        If self.dev_id exists get hardware for DeviceID
        """
        if self.dev_id == '':
            for element in self.wmi_system.Win32_Diskdrive(
                self.properties_to_get
            ):
                self.hardware_set.append(element)
        else:
            wql = 'SELECT {} FROM Win32_diskdrive WHERE PNPDeviceID LIKE "%{}%"'.format(
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
            item_ret = deepcopy(self.formatted_data)

            item_ret["description"] = hw_item['Description']
            item_ret["product"] = hw_item['Caption']
            item_ret["vendor"] = hw_item['Manufacturer']
            item_ret["deviceid"] = hw_item['DeviceID']
            item_ret["pnpdeviceid"] = hw_item['PNPDeviceID']
            item_ret["size"] = int(hw_item['Size'])
            item_ret["businfo"] = "scsi@{}:0.0.0".format(hw_item['Index'])

            if children:
                item_ret['children'] = PartitionDisk(
                    hw_item['DeviceID']
                ).format_data(children)

            ret.append(item_ret)

        return ret
