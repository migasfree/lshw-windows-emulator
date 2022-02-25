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


@HardwareClass.register('LogicalDisk')
class LogicalDisk(HardwareClass):
    """
    Gets logical disk information using WMI
    """

    def __init__(self, dev_id=''):
        super().__init__()

        self.formatted_data = {
            'id': self.__ERROR__,
            'class': 'volume',
            'claimed': True,
            'description': self.__ERROR__,
            'physid': '',
            'deviceid': self.__ERROR__,
            'logicalname': self.__ERROR__,
            'dev': '',
            'capacity': self.__ERROR__,
            'configuration': {
                'mount.fstype': self.__ERROR__,
                'mount.options': '',
                'state': 'mounted'
            }
        }

        self.dev_id = dev_id

        self.properties_to_get = [
            'Caption',
            'Name',
            'ProviderName',
            'Description',
            'FileSystem',
            'MediaType',
            'VolumeName',
            'Size',
            'FreeSpace',
            'DeviceID',
            'DriveType'
        ]

        self._update_properties_to_return()

    def get_hardware(self):
        """
        Get Hardware set
        If self.dev_id exists get hardware for DeviceID
        """

        if self.dev_id == '':
            # Gets everything
            for element in self.wmi_system.Win32_LogicalDisk(
                self.properties_to_get
            ):
                self.hardware_set.append(element)
        else:
            # Gets associated partitions to a disk (DeviceID = self.dev_id)
            wql = f'SELECT DeviceID FROM Win32_diskpartition WHERE DeviceID="{self.dev_id}"'
            for element in self.wmi_system.query(wql):
                for part in element.associators(
                    wmi_association_class='Win32_LogicalDiskToPartition',
                    wmi_result_class='Win32_LogicalDisk'
                ):
                    self.hardware_set.append(part)

        self.check_values()

    def format_data(self, children=False):
        self.get_hardware()

        drive_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

        ret = []
        for hw_item in self.hardware_set_to_return:
            try:
                _id = f'logicalvolume:{drive_letters.index(hw_item["DeviceID"][0])}'
            except ValueError:
                _id = self.__ERROR__

            file_system = hw_item.get('FileSystem', self.__DESC__)

            item_ret = deepcopy(self.formatted_data)
            item_ret['id'] = _id
            item_ret['deviceid'] = hw_item.get('DeviceID', self.__DESC__)
            item_ret['logicalname'] = hw_item.get('VolumeName', self.__DESC__)
            item_ret['capacity'] = hw_item.get('Size', self.__DESC__)
            if 'Description' in hw_item:
                item_ret['description'] = '{}. Volume name: [{}]. Label: {}. Filesystem: {}'.format(
                    hw_item['Description'],
                    hw_item.get('Name', self.__DESC__),
                    item_ret['logicalname'],
                    file_system
                )
            else:
                item_ret['description'] = self.__ERROR__
            item_ret['configuration']['mount.fstype'] = file_system

            ret.append(item_ret)

        return ret
