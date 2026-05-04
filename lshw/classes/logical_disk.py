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

from .hardware import Hardware
from .hardware_class import HardwareClass


@HardwareClass.register('LogicalDisk', parent='PartitionDisk')
class LogicalDisk(HardwareClass):
    """
    Gets logical disk information using WMI
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
            vendor='',
            physid='',
            serial='',
        )
        self.hardware.deviceid = self.__ERROR__
        self.hardware.logicalname = self.__ERROR__
        self.hardware.dev = ''
        self.hardware.capacity = self.__ERROR__
        self.hardware.configuration = {
            'mount.fstype': self.__ERROR__,
            'mount.options': '',
            'state': 'mounted',
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
            'DriveType',
        ]

        self._update_properties_to_return()

    def get_hardware(self):
        """
        Get Hardware set
        If self.dev_id exists get hardware for DeviceID
        """

        if self.dev_id == '':
            # Gets everything
            for element in self.wmi_system.Win32_LogicalDisk(self.properties_to_get):
                self.hardware_set.append(element)
        else:
            # Gets associated partitions to a disk (DeviceID = self.dev_id)
            self._validate_entity('Win32_LogicalDiskToPartition')
            self._validate_entity('Win32_LogicalDisk')
            success = False
            try:
                import re

                def _extract_id(ref):
                    if not ref:
                        return ''
                    if isinstance(ref, str):
                        match = re.search(r'DeviceID\s*=\s*"([^"]+)"', ref)
                        if match:
                            return match.group(1)
                        match = re.search(r"DeviceID\s*=\s*'([^']+)'", ref)
                        if match:
                            return match.group(1)
                        return ''
                    try:
                        return getattr(ref, 'DeviceID', '')
                    except Exception:
                        return ''

                for assoc in self.wmi_system.Win32_LogicalDiskToPartition():
                    try:
                        part_id = _extract_id(assoc.Antecedent)
                        if part_id.strip().lower() == self.dev_id.strip().lower():
                            ld_id = _extract_id(assoc.Dependent)
                            if ld_id:
                                wql = f'SELECT {self.build_wql_fields()} FROM Win32_LogicalDisk WHERE DeviceID="{self._sanitize_wql_value(ld_id)}"'
                                for ld in self.wmi_system.query(wql):
                                    self.hardware_set.append(ld)
                                success = True
                    except (AttributeError, TypeError, KeyError):
                        continue
            except Exception:
                pass

            if not success:
                # Fallback to the old associators method
                self._validate_entity('Win32_diskpartition')
                wql = (
                    f'SELECT DeviceID FROM Win32_diskpartition WHERE DeviceID="{self._sanitize_wql_value(self.dev_id)}"'
                )
                try:
                    for element in self.wmi_system.query(wql):
                        for part in element.associators(
                            wmi_association_class='Win32_LogicalDiskToPartition', wmi_result_class='Win32_LogicalDisk'
                        ):
                            self.hardware_set.append(part)
                except Exception:
                    pass

        self.check_values()

    def _populate_hardware(self, item_ret: Hardware, hw_item: dict) -> Hardware:
        drive_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

        try:
            item_ret.id = f'logicalvolume:{drive_letters.index(hw_item["DeviceID"][0])}'
        except ValueError:
            item_ret.id = self.__ERROR__

        file_system = hw_item.get('FileSystem', self.__DESC__)

        item_ret.deviceid = hw_item.get('DeviceID', self.__DESC__)
        item_ret.logicalname = hw_item.get('VolumeName', self.__DESC__)
        item_ret.capacity = hw_item.get('Size', self.__DESC__)

        if 'Description' in hw_item:
            item_ret.description = '{}. Volume name: [{}]. Label: {}. Filesystem: {}'.format(
                hw_item['Description'], hw_item.get('Name', self.__DESC__), item_ret.logicalname, file_system
            )

        item_ret.configuration['mount.fstype'] = file_system

        return item_ret
