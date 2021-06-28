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


@HardwareClass.register('SoundDevice')
class SoundDevice(HardwareClass):
    """
    Gets USB ports information using WMI
    """

    def __init__(self):
        HardwareClass.__init__(self)

        self.wmi_method = 'Win32_SoundDevice'

        self.formatted_data = {
            "id": "multimedia",
            "class": "multimedia",
            "claimed": True,
            "handle": "",
            "description": "Audio device",
            "product": self.__ERROR__,
            "vendor": self.__ERROR__,
            "physid": "",
            "businfo": "",
            "version": "",
            "width": 0,
            "clock": 0,
            "pnpdeviceid": self.__ERROR__,
            "deviceid": self.__ERROR__,
            "configuration": {
                "driver": "",
                "latency": ""
            },
            "capabilities": {
                "pm": "",
                "msi": "",
                "pciexpress": "",
                "bus_master": "",
                "cap_list": ""
            }
        }

        self.properties_to_get = [
            "PNPDeviceID",
            "DeviceID",
            "Manufacturer",
        ]

        self._update_properties_to_return()

    def format_data(self, children=False):
        self.get_hardware()

        ret = []
        for hw_item in self.hardware_set_to_return:
            item_ret = deepcopy(self.formatted_data)

            item_ret["product"] = hw_item.get('Manufacturer', self.__ERROR__)
            item_ret["pnpdeviceid"] = hw_item.get(
                'PNPDeviceID', self.__ERROR__
            )
            item_ret["deviceid"] = hw_item.get('DeviceID', self.__ERROR__)

            ret.append(item_ret)

        return ret
