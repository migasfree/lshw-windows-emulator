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
from typing import List

from .hardware import Hardware
from .hardware_class import HardwareClass, wmi

logger = logging.getLogger(__name__)


@HardwareClass.register('Pci', parent='BaseBoard')
class Pci(HardwareClass):
    """
    Gets PCI bus information using WMI
    """

    def __init__(self):
        super().__init__()

        self.wmi_method = 'Win32_Bus'

        self.hardware = Hardware(
            id='pci',
            class_='bridge',
            claimed=True,
            handle='',
            description='Host bridge',
            product='',
            vendor='',
            physid='',
        )
        self.hardware.businfo = ''
        self.hardware.version = ''
        self.hardware.width = 0
        self.hardware.clock = 0

        self.properties_to_get = [
            'Caption',
            'Description',
            'DeviceID',
        ]

        self._update_properties_to_return()

    def _populate_hardware(self, item_ret: Hardware, hw_item: dict) -> Hardware:
        id_bus = ''
        device_id = hw_item.get('DeviceID', '')
        if device_id:
            prefix = device_id[0:3].lower()
            if prefix in ('isa', 'pci', 'pnp'):
                id_bus = f'{prefix}:{device_id[-1]}'

        item_ret.id = id_bus
        item_ret.description = device_id if device_id else 'Host bridge'
        item_ret.product = hw_item.get('Caption', '')

        return item_ret

    def _fetch_children(self, hardware_list: List[Hardware]):
        # Pci itself is a list of bridge children.
        # But wait, the original Pci.format_data returns a list containing
        # a single top-level 'pci' Hardware object with ALL bridges as children.
        # My Template Method returns a list of items from hardware_set_to_return.
        # I need to override format_data for Pci to keep the single container behavior.
        pass

    def format_data(self, children=False):
        self.get_hardware()

        pci_bridges = []
        for hw_item in self.hardware_set_to_return:
            bridge = Hardware(id='', class_='bridge', claimed=True)
            bridge = self._populate_hardware(bridge, hw_item)
            pci_bridges.append(bridge)

        if children:
            for bridge in pci_bridges:
                for child_class in self.get_children(self._entity_):
                    try:
                        if child_class.__name__ == 'Usb':
                            for i, element in enumerate(child_class().format_data(children=True)):
                                element.id = f'usb:{i}'
                                pci_bridges.append(element)
                        else:
                            bridge.children.extend(child_class().format_data(children=True))
                    except (wmi.x_wmi, wmi.x_access_denied, AttributeError, KeyError, TypeError) as e:
                        logger.warning(f'Could not get children {child_class.__name__} for Pci: {e}')

            self.hardware.children = pci_bridges

        return [self.hardware]
