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


@HardwareClass.register('ComputerSystem')
class ComputerSystem(HardwareClass):
    """
    Gets ceneric computer system information using WMI
    """

    def __init__(self):
        super().__init__()

        self.wmi_method = 'Win32_computersystem'

        self.hardware = Hardware(
            id=self.__ERROR__,
            class_='system',
            claimed=True,
            handle='',
            description=self.__ERROR__,
            product=self.__ERROR__,
            vendor=self.__ERROR__,
            serial=self.__ERROR__,
        )
        # Extend base hardware with specific fields
        self.hardware.width = 0
        self.hardware.configuration = {
            'boot': '',
            'chassis': self.__ERROR__,
            'cpus': self.__ERROR__,
            'family': '',
            'sku': '',
            'uuid': self.__ERROR__,
        }

        self.properties_to_get = ['Model', 'Name', 'Description', 'Manufacturer', 'NumberOfProcessors']

        self._update_properties_to_return()

    def get_chassis(self):
        _chassis = self.__DESC__

        # Win32_SystemEnclosure
        chassis_types = [
            'Maybe Virtual Machine',
            '??',
            'Desktop',
            'low-profile',
            'Pizza Box',
            'mini-tower',
            'Full Tower',
            'Portable',
            'Laptop',
            'notebook',
            'Hand Held',
            'Docking Station',
            'All in One',
            'Sub Notebook',
            'Space-Saving',
            'Lunch Box',
            'Main System Chassis',
            'Lunch Box',
            'SubChassis',
            'Bus Expansion Chassis',
            'Peripheral Chassis',
            'Storage Chassis',
            'Rack Mount Unit',
            'Sealed-Case PC',
        ]

        for hw_item in self.wmi_system.Win32_SystemEnclosure(['ChassisTypes']):
            if type(hw_item.ChassisTypes).__name__ == 'NoneType':
                _chassis = self.__DESC__
            else:
                if int(hw_item.ChassisTypes[0]) in range(1, len(chassis_types) + 1):
                    _chassis = chassis_types[hw_item.ChassisTypes[0] - 1]

        return _chassis

    def get_computer_uuid_serialnumber(self):
        for hw_item in self.wmi_system.Win32_Computersystemproduct(['UUID', 'IdentifyingNumber']):
            uuid = hw_item.UUID if hw_item.UUID else self.__DESC__
            serial = hw_item.IdentifyingNumber if hw_item.IdentifyingNumber else self.__DESC__

        return [uuid, serial]

    def format_data(self, children=False):
        self.get_hardware()

        chassis = self.get_chassis()
        uuid, serial = self.get_computer_uuid_serialnumber()

        for hw_item in self.hardware_set_to_return:
            self.hardware.id = hw_item.get('Name', self.__ERROR__)
            self.hardware.description = '{}, {}'.format(hw_item.get('Description', self.__ERROR__), chassis)
            self.hardware.product = hw_item.get('Model', self.__ERROR__)
            self.hardware.vendor = hw_item.get('Manufacturer', self.__ERROR__)
            self.hardware.serial = serial
            self.hardware.configuration['chassis'] = chassis
            self.hardware.configuration['cpus'] = hw_item.get('NumberOfProcessors', self.__ERROR__)
            self.hardware.configuration['uuid'] = uuid

        if children:
            for child_class in self.get_children(self._entity_):
                try:
                    res = child_class().format_data(children)
                    if isinstance(res, list):
                        self.hardware.children.extend(res)
                    else:
                        self.hardware.children.append(res)
                except Exception as e:
                    logger.warning(f'Could not get children {child_class.__name__} for ComputerSystem: {e}')

        return self.hardware
