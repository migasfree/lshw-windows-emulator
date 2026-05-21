# Copyright (c) 2026 Jose Antonio Chavarría <jachavar@gmail.com>
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

import logging

from .hardware import Hardware
from .hardware_class import HardwareClass, wmi

logger = logging.getLogger(__name__)


@HardwareClass.register('Printer', parent='BaseBoard')
class Printer(HardwareClass):
    """
    Gets printer and print queue information using WMI
    """

    def __init__(self):
        super().__init__()

        self.hardware = Hardware(
            id=self.__ERROR__,
            class_='printer',
            claimed=True,
            handle='',
            description='Printer',
            product=self.__ERROR__,
            vendor=self.__ERROR__,
            physid='',
            serial='',
        )
        self.hardware.logicalname = ''
        self.hardware.configuration = {
            'network': '',
            'local': '',
        }

        self.properties_to_get = [
            'DeviceID',
            'Name',
            'Caption',
            'DriverName',
            'PortName',
            'Network',
            'Local',
        ]

        self._update_properties_to_return()
        self._printer_id = 0

    def get_hardware(self):
        try:
            self._validate_entity('Win32_Printer')
            wql = self.build_wql_select('Win32_Printer')
            self.execute_wql_query(wql)
        except (wmi.x_wmi, AttributeError, ValueError) as e:
            logger.debug(f'Could not query Win32_Printer: {e}')

        self.check_values()

    def _populate_hardware(self, item_ret: Hardware, hw_item: dict) -> Hardware:
        item_ret.id = f'printer:{self._printer_id}'
        self._printer_id += 1

        desc = hw_item.get('Caption')
        if not desc or desc == self.__DESC__:
            desc = hw_item.get('Name', 'Printer')
        item_ret.description = desc

        item_ret.product = hw_item.get('DriverName', self.__ERROR__)

        # Try to infer manufacturer from driver or name
        prod_lower = str(item_ret.product).lower()
        if 'hp' in prod_lower or 'hewlett' in prod_lower:
            item_ret.vendor = 'HP'
        elif 'epson' in prod_lower:
            item_ret.vendor = 'Epson'
        elif 'canon' in prod_lower:
            item_ret.vendor = 'Canon'
        elif 'brother' in prod_lower:
            item_ret.vendor = 'Brother'
        elif 'lexmark' in prod_lower:
            item_ret.vendor = 'Lexmark'
        elif 'xerox' in prod_lower:
            item_ret.vendor = 'Xerox'
        elif 'ricoh' in prod_lower:
            item_ret.vendor = 'Ricoh'
        elif 'pdf' in prod_lower:
            item_ret.vendor = 'Software'
        else:
            item_ret.vendor = self.__DESC__

        port = hw_item.get('PortName')
        if port and port != self.__DESC__:
            item_ret.logicalname = str(port).strip()

        net = hw_item.get('Network')
        if net is not None and net != self.__DESC__:
            item_ret.configuration['network'] = str(net).lower()

        local = hw_item.get('Local')
        if local is not None and local != self.__DESC__:
            item_ret.configuration['local'] = str(local).lower()

        return item_ret
