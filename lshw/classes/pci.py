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

    def format_data(self, children=False):
        self.get_hardware()

        pci_child = []
        for hw_item in self.hardware_set_to_return:
            id_bus = ''
            if 'DeviceID' in hw_item:
                if hw_item['DeviceID'][0:3].lower() == 'isa':
                    id_bus = f'isa:{hw_item["DeviceID"][-1]}'
                elif hw_item['DeviceID'][0:3].lower() == 'pci':
                    id_bus = f'pci:{hw_item["DeviceID"][-1]}'
                elif hw_item['DeviceID'][0:3].lower() == 'pnp':
                    id_bus = f'pnp:{hw_item["DeviceID"][-1]}'

            child = Hardware(
                id=id_bus,
                class_='bridge',
                claimed=True,
                handle='',
                description=hw_item.get('DeviceID', 'Host bridge'),
                product=hw_item.get('Caption', ''),
                vendor='',
                physid='',
            )
            child.businfo = ''
            child.version = ''
            child.width = 0
            child.clock = 0

            pci_child.append(child)

        if children:
            for child_class in self.get_children(self._entity_):
                try:
                    # Handle Usb specifically if needed for ID formatting
                    if child_class.__name__ == 'Usb':
                        # child_class().format_data(children) returns List[Hardware]
                        for i, element in enumerate(child_class().format_data(children)):
                            element.id = f'usb:{i}'
                            pci_child.append(element)
                    else:
                        res = child_class().format_data(children)
                        if isinstance(res, list):
                            pci_child.extend(res)
                        else:
                            pci_child.append(res)
                except Exception as e:
                    logger.warning(f'Could not get children {child_class.__name__} for Pci: {e}')

            self.hardware.children = pci_child

        return self.hardware
