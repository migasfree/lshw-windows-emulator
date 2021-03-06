# -*- coding: UTF-8 -*-

# Copyright (c) 2021-2022 Jose Antonio Chavarría <jachavar@gmail.com>
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
from .logical_disk import LogicalDisk


@HardwareClass.register('PartitionDisk')
class PartitionDisk(HardwareClass):
    """
    Gets partition disk information using WMI
    """

    def __init__(self, dev_id=''):
        super().__init__()

        self.formatted_data = {
            'id': self.__ERROR__,
            'class': 'volume',
            'claimed': True,
            'description': self.__ERROR__,
            'vendor': 'Windows',
            'physid': '',
            'businfo': '',
            'logicalname': '',
            'dev': '',
            'version': '',
            'serial': '',
            'size': 0,
            'capacity': 0,
            'PNPDeviceID': self.__ERROR__,
            'DeviceID': self.__ERROR__,
            'configuration': {
                'filesystem': 'fat',
                'modified': '',
                'mount.fstype': 'fat',
                'mount.options': '',
                'mounted': '',
                'state': 'mounted'
            },
            'capabilities': {
                'primary': self.__ERROR__,
                'extended': self.__ERROR__,
                'bootable': self.__ERROR__,
                'extended_attributes': ''
            },
            'children': []
        }

        self.dev_id = dev_id

        self.properties_to_get = [
            'Bootable',
            'BootPartition',
            'DeviceID',
            'PNPDeviceID',
            'Index',
            'Type',
            'Size',
            'Description',
            'PrimaryPartition',
        ]

        self._update_properties_to_return()

    def get_hardware(self):
        """
        Get Hardware set
        If self.dev_id exists get hardware for DeviceID
        """
        if self.dev_id == '':
            # Gets everything
            for element in self.wmi_system.Win32_Diskpartition(
                self.properties_to_get
            ):
                self.hardware_set.append(element)
        else:
            # Gets associated partitions to a disk (DeviceID = self.dev_id)
            wql = f'SELECT DeviceID FROM Win32_diskdrive WHERE DeviceID="{self.dev_id}"'
            for element in self.wmi_system.query(wql):
                for part in element.associators('Win32_DiskDriveToDiskPartition'):
                    self.hardware_set.append(part)

        self.check_values()

    def format_data(self, children=False):
        self.get_hardware()

        ret = []
        for hw_item in self.hardware_set_to_return:
            bootable = 'No bootable partition'
            if 'Bootable' in hw_item and hw_item['Bootable'] is True:
                bootable = 'Bootable partition'

            if 'BootPartition' in hw_item and hw_item['BootPartition'] is True:
                bootable += ' (active)'

            primary = 'No primary partition'
            extended = 'Extended partition'
            if 'PrimaryPartition' in hw_item \
                    and hw_item['PrimaryPartition'] is True:
                primary = 'Primary partition'
                extended = 'No extended partition'

            description = hw_item.get('Description', self.__ERROR__)
            if hw_item['Description'].lower() == 'unknown' \
                    and hw_item['Bootable'] is True \
                    and hw_item['BootPartition'] is True:
                description = 'Primary. Bootable. Boot partition. FAT32'

            item_ret = deepcopy(self.formatted_data)

            item_ret['id'] = f'volume:{hw_item["Index"]}'
            item_ret['size'] = hw_item['Size']
            item_ret['capacity'] = int(hw_item['Size'])
            item_ret['PNPDeviceID'] = hw_item['PNPDeviceID']
            item_ret['DeviceID'] = hw_item['DeviceID']
            item_ret['description'] = description
            item_ret['capabilities']['primary'] = primary
            item_ret['capabilities']['extended'] = extended
            item_ret['capabilities']['bootable'] = bootable

            if children:
                item_ret['children'] = LogicalDisk(
                    hw_item['DeviceID']
                ).format_data(children)

            ret.append(item_ret)

        return ret
