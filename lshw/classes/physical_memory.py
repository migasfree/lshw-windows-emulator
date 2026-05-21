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
from .hardware_class import HardwareClass, wmi

logger = logging.getLogger(__name__)


@HardwareClass.register('PhysicalMemory', parent='BaseBoard')
class PhysicalMemory(HardwareClass):
    """
    Gets physical memory information using WMI
    """

    def __init__(self):
        super().__init__()

        self.wmi_method = 'Win32_physicalMemory'

        self.hardware = Hardware(
            id='memory:0',
            class_='memory',
            claimed=True,
            handle='',
            description='System Memory',
            physid='',
        )
        self.hardware.slot = ''

        self.properties_to_get = [
            'Tag',
            'DeviceLocator',
            'Capacity',
            'Speed',
            'MemoryType',
            'SMBIOSMemoryType',
            'DataWidth',
            'Manufacturer',
            'SerialNumber',
            'PartNumber',
        ]

        self._update_properties_to_return()

    def _populate_hardware(self, item_ret: Hardware, hw_item: dict) -> Hardware:
        # PhysicalMemory is a bit special: it populates children of self.hardware
        # but the Template Method expects to return individual items.
        # We'll adapt it to return the 'bank' as if it were the main item.

        memory_types = {
            0: 'Unknown',
            1: 'Other',
            2: 'DRAM',
            3: 'Synchronous DRAM',
            4: 'Cache DRAM',
            5: 'EDO',
            6: 'EDRAM',
            7: 'VRAM',
            8: 'SRAM',
            9: 'RAM',
            10: 'ROM',
            11: 'Flash',
            12: 'EEPROM',
            13: 'FEPROM',
            14: 'EPROM',
            15: 'CDRAM',
            16: '3DRAM',
            17: 'SDRAM',
            18: 'SGRAM',
            19: 'RDRAM',
            20: 'DDR',
            21: 'DDR2',
            22: 'DDR2 FB-DIMM',
            24: 'DDR3',
            25: 'FBD2',
            26: 'DDR4',
            27: 'LPDDR',
            28: 'LPDDR2',
            29: 'LPDDR3',
            30: 'LPDDR4',
            31: 'Logical DDR4',
            32: 'LPDDR4X',
            34: 'DDR5',
            35: 'LPDDR5',
        }

        mem_type_idx = hw_item.get('SMBIOSMemoryType')
        if not mem_type_idx or mem_type_idx == self.__DESC__ or mem_type_idx == 0:
            mem_type_idx = hw_item.get('MemoryType')

        try:
            mem_type_idx = int(mem_type_idx)
            mem_type_str = memory_types.get(mem_type_idx, 'Unknown')
        except (ValueError, TypeError):
            mem_type_str = 'Unknown'

        part = hw_item.get('PartNumber')
        if part and part != self.__DESC__:
            part_str = str(part).strip()
            item_ret.product = f'{mem_type_str} (Part: {part_str})'
        else:
            item_ret.product = mem_type_str

        item_ret.id = f'bank:{hw_item["Tag"][-1]}' if 'Tag' in hw_item else self.__ERROR__
        item_ret.description = hw_item.get('Tag', self.__ERROR__)
        item_ret.slot = hw_item.get('DeviceLocator', self.__ERROR__)
        item_ret.units = 'bytes'
        item_ret.size = hw_item.get('Capacity', 0)
        item_ret.width = hw_item.get('DataWidth', 0)
        item_ret.clock = hw_item.get('Speed', 0)
        item_ret.vendor = hw_item.get('Manufacturer', self.__ERROR__)

        serial = hw_item.get('SerialNumber')
        if serial and serial != self.__DESC__:
            item_ret.serial = str(serial).strip()
        else:
            item_ret.serial = ''

        return item_ret

    def format_data(self, children=False):
        # Override format_data because PhysicalMemory results are
        # actually children of a parent container 'memory:0'
        self.get_hardware()

        if self.hardware_set_to_return:
            for hw_item in self.hardware_set_to_return:
                bank = Hardware(id='', class_='memory', claimed=True)
                bank = self._populate_hardware(bank, hw_item)
                self.hardware.children.append(bank)
        else:
            # Fallback to TotalPhysicalMemory if no banks found
            try:
                for item in self.wmi_system.Win32_ComputerSystem(['TotalPhysicalMemory']):
                    bank = Hardware(
                        id='bank:0',
                        class_='memory',
                        claimed=True,
                        description='System Memory',
                        product='System Memory',
                        slot='System Board',
                        size=int(item.TotalPhysicalMemory),
                        width=64,
                        clock=0,
                    )
                    bank.units = 'bytes'
                    self.hardware.children.append(bank)
            except (wmi.x_wmi, wmi.x_access_denied, AttributeError, KeyError, TypeError) as e:
                logger.error(f'Error getting memory from Win32_ComputerSystem: {e}')

        return [self.hardware]
