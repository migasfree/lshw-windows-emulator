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


@HardwareClass.register('Usb', parent='Pci')
class Usb(HardwareClass):
    """
    Gets USB ports information using WMI
    """

    def __init__(self):
        super().__init__()

        self.wmi_method = 'Win32_USBController'

        self.hardware = Hardware(
            id='',
            class_='bus',
            claimed=True,
            handle='',
            description=self.__ERROR__,
            product='',
            vendor=self.__ERROR__,
            physid='',
            serial='',
        )
        self.hardware.businfo = ''
        self.hardware.version = ''
        self.hardware.width = 0
        self.hardware.clock = 0
        self.hardware.pnpdeviceid = self.__ERROR__
        self.hardware.configuration = {'driver': '', 'latency': ''}
        self.hardware.capabilities = {'uhci': '', 'bus_master': ''}

        self.properties_to_get = ['PNPDeviceID', 'DeviceID', 'Description', 'Manufacturer']

        self._update_properties_to_return()

    def format_data(self, children=False):
        self.get_hardware()

        ret = []
        for hw_item in self.hardware_set_to_return:
            item_ret = Hardware(
                id='',
                class_='bus',
                claimed=True,
                handle='',
                description=hw_item.get('Description', self.__ERROR__),
                product='',
                vendor=hw_item.get('Manufacturer', self.__ERROR__),
                physid='',
                serial='',
            )
            item_ret.businfo = ''
            item_ret.version = ''
            item_ret.width = 0
            item_ret.clock = 0
            item_ret.pnpdeviceid = hw_item.get('PNPDeviceID', self.__ERROR__)
            item_ret.configuration = {'driver': '', 'latency': ''}
            item_ret.capabilities = {'uhci': '', 'bus_master': ''}

            if children and 'PNPDeviceID' in hw_item:
                try:
                    # UsbDevice returns List[Hardware]
                    item_ret.children = self.factory('UsbDevice')(dev_id=[hw_item['PNPDeviceID']]).format_data(children)
                except Exception as e:
                    logger.warning(f'Could not get children for Usb {hw_item["PNPDeviceID"]}: {e}')

            ret.append(item_ret)

        return ret
