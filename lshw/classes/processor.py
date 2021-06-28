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


@HardwareClass.register('Processor')
class Processor(HardwareClass):
    """
    Gets processor/CPU information using WMI
    """

    def __init__(self):
        HardwareClass.__init__(self)

        self.wmi_method = 'Win32_processor'

        self.formatted_data = {
            "id": self.__ERROR__,
            "class": "processor",
            "claimed": True,
            "handle": "",
            "description": self.__ERROR__,
            "product": self.__ERROR__,
            "vendor": self.__ERROR__,
            "physid": "",
            "businfo": "cpu@",
            "version": "",
            "serial": "",
            "slot": self.__ERROR__,
            "units": "Hz",
            "size": 0,
            "width": self.__ERROR__,
            "clock": self.__ERROR__
        }

        self.properties_to_get = [
            "Manufacturer",
            "Name",
            "Description",
            "SocketDesignation",
            "DataWidth",
            "MaxClockSpeed",
        ]

        self._update_properties_to_return()

    def format_data(self, children=False):
        self.get_hardware()

        ret = []
        cpu_id = 0
        for hw_item in self.hardware_set_to_return:
            item_ret = deepcopy(self.formatted_data)

            item_ret["id"] = 'cpu:{}'.format(cpu_id)
            item_ret["description"] = hw_item.get(
                'Description', self.__ERROR__
            )
            item_ret["product"] = hw_item.get('Name', self.__ERROR__)
            item_ret["vendor"] = hw_item.get('Manufacturer', self.__ERROR__)
            item_ret["slot"] = hw_item.get('SocketDesignation', self.__ERROR__)
            item_ret["width"] = hw_item.get('DataWidth', self.__ERROR__)
            item_ret["clock"] = hw_item.get('MaxClockSpeed', self.__ERROR__)

            ret.append(item_ret)
            cpu_id += 1

        return ret
