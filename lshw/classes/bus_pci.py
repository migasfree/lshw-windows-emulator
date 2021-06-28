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
from .ide import Ide
from .usb import Usb
from .sound_device import SoundDevice
from .graphic_card import GraphicCard
from .network_card import NetworkCard


@HardwareClass.register('BusPci')
class BusPci(HardwareClass):
    """
    Gets PCI bus information using WMI
    """

    def __init__(self):
        HardwareClass.__init__(self)

        self.wmi_method = 'Win32_Bus'

        self.formatted_data = {
            'id': 'pci',
            'class': 'bridge',
            'claimed': True,
            'handle': '',
            'description': 'Host bridge',
            'product': '',
            'vendor': '',
            'physid': '',
            'businfo': '',
            'version': '',
            'width': 0,
            'clock': 0,
            'children': []
        }

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
                    id_bus = 'isa:{}'.format(hw_item['DeviceID'][-1])
                elif hw_item['DeviceID'][0:3].lower() == 'pci':
                    id_bus = 'pci:{}'.format(hw_item['DeviceID'][-1])
                elif hw_item['DeviceID'][0:3].lower() == 'pnp':
                    id_bus = 'pnp:{}'.format(hw_item['DeviceID'][-1])

            child = deepcopy(self.formatted_data)
            child['id'] = id_bus
            child['description'] = hw_item.get('DeviceID', 'Host bridge')
            child['product'] = hw_item.get('Caption', '')

            pci_child.append(child)

        if children:
            for element in Ide().format_data(children):
                pci_child.append(element)

            for element in NetworkCard().format_data():
                pci_child.append(element)

            for element in GraphicCard().format_data():
                pci_child.append(element)

            i = 0
            for element in Usb().format_data(children):
                element['id'] = 'usb:{}'.format(i)
                pci_child.append(element)
                i += 1

            for element in SoundDevice().format_data():
                pci_child.append(element)

            self.formatted_data['children'] = pci_child

        return self.formatted_data
