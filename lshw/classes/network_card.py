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
import platform

from .hardware import Hardware
from .hardware_class import HardwareClass

logger = logging.getLogger(__name__)


@HardwareClass.register('NetworkCard', parent='Pci')
class NetworkCard(HardwareClass):
    """
    Gets network card information using WMI
    """

    def __init__(self):
        super().__init__()

        self.hardware = Hardware(
            id='network',
            class_='network',
            claimed=True,
            handle='',
            description='Ethernet interface',
            product=self.__ERROR__,
            vendor=self.__ERROR__,
            physid='',
            serial=self.__ERROR__,
        )
        self.hardware.businfo = ''
        self.hardware.logicalname = self.__ERROR__
        self.hardware.version = ''
        self.hardware.units = 'bit/s'
        self.hardware.size = 0
        self.hardware.capacity = 0
        self.hardware.width = 0
        self.hardware.clock = 0
        self.hardware.pnpdeviceid = self.__ERROR__
        self.hardware.configuration = {
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
            'speed': self.__ERROR__,
        }
        self.hardware.capabilities = {
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
            'autonegotiation': self.__ERROR__,
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
            'PNPDeviceID',
            'Index',
            'NetConnectionStatus',
            'ServiceName',
        ]

        self._update_properties_to_return()

    def get_hardware(self):
        where_clause = '(NOT PNPDeviceID LIKE "%ROOT%")'
        # wql is different in 10.0.18362 builds and later
        if platform.release() == '10' and platform.version() >= '10.0.18362':
            where_clause = '(PhysicalAdapter=True)'

        wql = self.build_wql_select('Win32_NetworkAdapter', where_clause)
        self.execute_wql_query(wql)
        self.check_values()

        # Query IP Addresses from Win32_NetworkAdapterConfiguration
        self.ip_lookup = {}
        try:
            configs = self.wmi_system.query('SELECT Index, IPAddress FROM Win32_NetworkAdapterConfiguration')
            for c in configs:
                idx = getattr(c, 'Index', None)
                ips = getattr(c, 'IPAddress', None)
                if idx is not None and ips:
                    self.ip_lookup[idx] = ips[0]
        except Exception as e:
            logger.debug('Could not query Win32_NetworkAdapterConfiguration: %s', e, exc_info=True)

    def _populate_hardware(self, item_ret: Hardware, hw_item: dict) -> Hardware:
        item_ret.product = hw_item.get('Description', self.__ERROR__)
        item_ret.vendor = hw_item.get('Manufacturer', self.__ERROR__)
        item_ret.serial = hw_item.get('MACAddress', self.__ERROR__)
        item_ret.logicalname = hw_item.get('NetConnectionID', self.__ERROR__)
        item_ret.pnpdeviceid = hw_item.get('PNPDeviceID', self.__ERROR__)

        item_ret.configuration['autonegotiation'] = hw_item.get('Autosense', self.__DESC__)
        item_ret.configuration['speed'] = hw_item.get('Speed', self.__ERROR__)

        item_ret.capabilities['autonegotiation'] = hw_item.get('Autosense', self.__DESC__)

        # Set driver (ServiceName)
        driver = hw_item.get('ServiceName')
        if driver and driver != self.__DESC__:
            item_ret.configuration['driver'] = str(driver).strip()

        # Set link status from NetConnectionStatus (2 = connected)
        status = hw_item.get('NetConnectionStatus')
        if status is not None and status != self.__DESC__:
            try:
                status_int = int(status)
                item_ret.configuration['link'] = 'yes' if status_int == 2 else 'no'
            except (ValueError, TypeError):
                item_ret.configuration['link'] = 'no'
        else:
            item_ret.configuration['link'] = 'no'

        # Set IP Address from lookup table
        idx = hw_item.get('Index')
        if idx is not None and idx in getattr(self, 'ip_lookup', {}):
            item_ret.configuration['ip'] = self.ip_lookup[idx]

        return item_ret
