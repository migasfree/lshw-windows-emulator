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


@HardwareClass.register('PhysicalDisk', parent=['Ide'])
class PhysicalDisk(HardwareClass):
    """
    Gets physical disk information using WMI
    """

    def __init__(self, dev_id=''):
        super().__init__()

        self.dev_id = dev_id

        self.hardware = Hardware(
            id='disk',
            class_='disk',
            claimed=True,
            handle='',
            description=self.__ERROR__,
            product=self.__ERROR__,
            vendor=self.__ERROR__,
            physid='',
            serial='',
        )
        self.hardware.deviceid = self.__ERROR__
        self.hardware.pnpdeviceid = self.__ERROR__
        self.hardware.businfo = self.__ERROR__
        self.hardware.logicalname = ''
        self.hardware.dev = ''
        self.hardware.version = ''
        self.hardware.units = 'bytes'
        self.hardware.size = 0
        self.hardware.configuration = {'ansiversion': '', 'signature': ''}
        self.hardware.capabilities = {'partitioned': '', 'partitioned:dos': ''}

        self.properties_to_get = [
            'Caption',
            'Description',
            'DeviceID',
            'Index',
            'Manufacturer',
            'PNPDeviceID',
            'Size',
        ]

        self._update_properties_to_return()

    def get_hardware(self):
        """
        Get Hardware set
        If self.dev_id exists get hardware for DeviceID
        """
        if self.dev_id == '':
            for element in self.wmi_system.Win32_Diskdrive(self.properties_to_get):
                self.hardware_set.append(element)
        else:
            wql = self.build_wql_select('Win32_diskdrive', f'PNPDeviceID LIKE "%{self.dev_id}%"')
            self.execute_wql_query(wql)

        self.check_values()

    def _populate_hardware(self, item_ret: Hardware, hw_item: dict) -> Hardware:
        item_ret.description = hw_item['Description']
        item_ret.product = hw_item['Caption']
        item_ret.vendor = hw_item['Manufacturer']
        item_ret.deviceid = hw_item['DeviceID']
        item_ret.pnpdeviceid = hw_item['PNPDeviceID']
        item_ret.businfo = f'scsi@{hw_item["Index"]}:0.0.0'

        try:
            raw_size = int(hw_item['Size'])
            logger.info(f'Disk {hw_item["DeviceID"]} raw size from WMI: {raw_size}')
            item_ret.size = raw_size
        except (ValueError, TypeError, KeyError) as e:
            logger.warning(f'Could not parse size for disk {hw_item.get("DeviceID", "unknown")}: {e}')
            item_ret.size = 0

        return item_ret

    def _fetch_children(self, hardware_list):
        for hw_instance in hardware_list:
            try:
                # PartitionDisk returns List[Hardware]
                hw_instance.children = self.factory('PartitionDisk')(hw_instance.deviceid).format_data(children=True)
            except (wmi.x_wmi, wmi.x_access_denied, AttributeError, KeyError, TypeError) as e:
                logger.warning(f'Could not get children for PhysicalDisk {hw_instance.deviceid}: {e}')
