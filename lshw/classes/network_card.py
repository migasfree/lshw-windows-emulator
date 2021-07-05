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

import platform

from copy import deepcopy

from .hardware_class import HardwareClass


@HardwareClass.register('NetworkCard')
class NetworkCard(HardwareClass):
    """
    Gets network card information using WMI
    """

    def __init__(self):
        super().__init__()

        self.formatted_data = {
            'id': 'network',
            'class': 'network',
            'claimed': True,
            'handle': '',
            'description': 'Ethernet interface',
            'product': self.__ERROR__,
            'vendor': self.__ERROR__,
            'physid': '',
            'businfo': '',
            'logicalname': self.__ERROR__,
            'version': '',
            'serial': self.__ERROR__,
            'units': 'bit/s',
            'size': 0,
            'capacity': 0,
            'width': 0,
            'clock': 0,
            'pnpdeviceid':  self.__ERROR__,
            'configuration': {
                'autonegotiation': self.__ERROR__,
                'broadcast': '',
                'driver': '',
                'driverversion': '',
                'duplex': '',
                'firmware': '',
                'ip': '',
                'latency': '',
                'link': '',
                'multicast': '',
                'port': '',
                'speed': self.__ERROR__
            },
            'capabilities': {
                'pm': '',
                'vpd': '',
                'msi': '',
                'pciexpress': '',
                'bus_master': '',
                'cap_list': '',
                'ethernet': True,
                'physical': '',
                'tp': '',
                '10bt': '',
                '10bt-fd': '',
                '100bt': '',
                '100bt-fd': '',
                '1000bt': '',
                '1000bt-fd': '',
                'autonegotiation': self.__ERROR__
            }
        }

        self.properties_to_get = [
            'Speed',
            'SystemCreationClassName',
            'AdapterType',
            'Autosense',
            'Caption',
            'MACAddress',
            'ProductName',
            'Manufacturer',
            'NetConnectionID',
            'Description',
            'PNPDeviceID'
        ]

        self._update_properties_to_return()

    def get_hardware(self):
        fields = ','.join(self.properties_to_get)

        wql = 'SELECT {} FROM Win32_NetworkAdapter WHERE (NOT PNPDeviceID LIKE "%ROOT%")'.format(fields)
        # wql is diferent in 10.0.18362 compilations and later
        if platform.release() == '10' and platform.version() >= '10.0.18362':
            wql = 'SELECT {} FROM Win32_NetworkAdapter WHERE (PhysicalAdapter=True)'.format(fields)

        for element in self.wmi_system.query(wql):
            self.hardware_set.append(element)

        self.check_values()

    def format_data(self, children=False):
        self.get_hardware()

        ret = []
        for hw_item in self.hardware_set_to_return:
            item_ret = deepcopy(self.formatted_data)

            item_ret['product'] = hw_item.get('Description', self.__ERROR__)
            item_ret['vendor'] = hw_item.get('Manufacturer', self.__ERROR__)
            item_ret['logicalname'] = hw_item.get(
                'NetConnectionID', self.__ERROR__
            )
            item_ret['serial'] = hw_item.get('MACAddress', self.__ERROR__)
            item_ret['pnpdeviceid'] = hw_item.get(
                'PNPDeviceID', self.__ERROR__
            )
            item_ret['configuration']['autonegotiation'] = hw_item.get(
                'Autosense', self.__DESC__
            )
            item_ret['configuration']['speed'] = hw_item.get(
                'Speed', self.__ERROR__
            )
            item_ret['capabilities']['autonegotiation'] = hw_item.get(
                'Autosense', self.__DESC__
            )

            ret.append(item_ret)

        return ret
