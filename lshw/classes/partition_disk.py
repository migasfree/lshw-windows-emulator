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


@HardwareClass.register('PartitionDisk', parent='PhysicalDisk')
class PartitionDisk(HardwareClass):
    """
    Gets partition disk information using WMI
    """

    def __init__(self, dev_id=''):
        super().__init__()

        self.hardware = Hardware(
            id=self.__ERROR__,
            class_='volume',
            claimed=True,
            handle='',
            description=self.__ERROR__,
            product='',
            vendor='Windows',
            physid='',
            serial='',
        )
        self.hardware.businfo = ''
        self.hardware.logicalname = ''
        self.hardware.dev = ''
        self.hardware.version = ''
        self.hardware.size = 0
        self.hardware.capacity = 0
        self.hardware.pnpdeviceid = self.__ERROR__
        self.hardware.deviceid = self.__ERROR__
        self.hardware.configuration = {
            'filesystem': 'fat',
            'modified': '',
            'mount.fstype': 'fat',
            'mount.options': '',
            'mounted': '',
            'state': 'mounted',
        }
        self.hardware.capabilities = {
            'primary': self.__ERROR__,
            'extended': self.__ERROR__,
            'bootable': self.__ERROR__,
            'extended_attributes': '',
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
            for element in self.wmi_system.Win32_Diskpartition(self.properties_to_get):
                self.hardware_set.append(element)
        else:
            # Gets associated partitions to a disk (DeviceID = self.dev_id)
            self._validate_entity('Win32_diskdrive')
            wql = f'SELECT DeviceID FROM Win32_diskdrive WHERE DeviceID="{self._sanitize_wql_value(self.dev_id)}"'
            for element in self.wmi_system.query(wql):
                for part in element.associators('Win32_DiskDriveToDiskPartition'):
                    self.hardware_set.append(part)

        self.check_values()

    def _populate_hardware(self, item_ret: Hardware, hw_item: dict) -> Hardware:
        bootable = 'No bootable partition'
        if 'Bootable' in hw_item and hw_item['Bootable'] is True:
            bootable = 'Bootable partition'

        if 'BootPartition' in hw_item and hw_item['BootPartition'] is True:
            bootable += ' (active)'

        primary = 'No primary partition'
        extended = 'Extended partition'
        if 'PrimaryPartition' in hw_item and hw_item['PrimaryPartition'] is True:
            primary = 'Primary partition'
            extended = 'No extended partition'

        description = hw_item.get('Description', self.__ERROR__)
        if (
            hw_item.get('Description', '').lower() == 'unknown'
            and hw_item.get('Bootable') is True
            and hw_item.get('BootPartition') is True
        ):
            description = 'Primary. Bootable. Boot partition. FAT32'

        item_ret.id = f'volume:{hw_item["Index"]}'
        item_ret.description = description
        item_ret.size = hw_item['Size']
        item_ret.capacity = int(hw_item['Size'])
        item_ret.pnpdeviceid = hw_item['PNPDeviceID']
        item_ret.deviceid = hw_item['DeviceID']

        item_ret.capabilities['primary'] = primary
        item_ret.capabilities['extended'] = extended
        item_ret.capabilities['bootable'] = bootable

        return item_ret

    def _fetch_children(self, hardware_list):
        for hw_instance in hardware_list:
            try:
                # LogicalDisk returns List[Hardware]
                hw_instance.children = self.factory('LogicalDisk')(hw_instance.deviceid).format_data(children=True)
            except (wmi.x_wmi, wmi.x_access_denied, AttributeError, KeyError, TypeError) as e:
                logger.warning(f'Could not get children for PartitionDisk {hw_instance.deviceid}: {e}')
