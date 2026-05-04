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


@HardwareClass.register('Ide', parent='Pci')
class Ide(HardwareClass):
    """
    Gets the relationship between IDE controllers
    """

    def __init__(self):
        super().__init__()

        self.hardware = Hardware(
            id='ide:0',
            class_='',
            claimed=True,
            handle='',
            description=self.__ERROR__,
            product=self.__ERROR__,
            vendor=self.__ERROR__,
            physid='',
            serial='',
        )
        self.hardware.businfo = ''
        self.hardware.logicalname = ''
        self.hardware.version = ''
        self.hardware.width = 0
        self.hardware.clock = 0
        self.hardware.pnpdeviceid = self.__ERROR__

        self.properties_to_get = ['Manufacturer', 'Caption', 'Description', 'DeviceID', 'PNPDeviceID']

        self._update_properties_to_return()
        self._ide_results = []
        self._cached_disk_pnp_ids = set()

    def get_hardware(self):
        ide_controller_device_set = []
        ide_controller_device_primary = []
        for ide_assoc in self.wmi_system.Win32_IDEControllerdevice(['Antecedent', 'Dependent']):
            ant_value = ide_assoc.antecedent.split('=')[1].replace('"', '').replace('\\\\', '\\')
            dep_value = ide_assoc.dependent.split('=')[1].replace('"', '').replace('\\\\', '\\')

            if ant_value[0:4] == 'PCI\\' and ant_value not in ide_controller_device_primary:
                ide_controller_device_primary.append(ant_value)

            ide_controller_device_set.append({'ant_value': ant_value, 'dep_value': dep_value})

        self._ide_results = []
        id_cont_prim = 0
        for element in ide_controller_device_primary:
            wql = self.build_wql_select('Win32_IDEController', f'PNPDeviceID="{self._sanitize_wql_value(element)}"')
            for ide in self.wmi_system.query(wql):
                primary_controller = Hardware(
                    id=f'ide:{id_cont_prim}',
                    class_='',
                    claimed=True,
                    description=ide.Description,
                    product=ide.Caption,
                    vendor=ide.Manufacturer,
                )
                primary_controller.pnpdeviceid = ide.PNPDeviceID
                id_cont_prim += 1

                for assoc in ide_controller_device_set:
                    if assoc['ant_value'] == ide.PNPDeviceID:
                        wql2 = self.build_wql_select(
                            'Win32_IDEController', f'PNPDeviceID="{self._sanitize_wql_value(assoc["dep_value"])}"'
                        )
                        for ide2 in self.wmi_system.query(wql2):
                            secondary_controller = Hardware(
                                id=f'channel:{ide2.PNPDeviceID[-1]}',
                                class_='',
                                claimed=True,
                                description=ide2.Description,
                                product=ide2.Caption,
                                vendor=ide2.Manufacturer,
                            )
                            secondary_controller.pnpdeviceid = ide2.PNPDeviceID
                            primary_controller.children.append(secondary_controller)

                self._ide_results.append(primary_controller)

    def _populate_hardware(self, item_ret: Hardware, hw_item: dict) -> Hardware:
        """
        Ide uses a custom format_data loop, but we implement this to
        satisfy the abstract base class requirement.
        """
        return item_ret

    def format_data(self, children=False):
        try:
            self._cached_disk_pnp_ids = set()
            try:
                self._validate_entity('Win32_diskdrive')
                for d in self.wmi_system.Win32_diskdrive(['PNPDeviceID']):
                    if getattr(d, 'PNPDeviceID', None):
                        self._cached_disk_pnp_ids.add(d.PNPDeviceID.strip().replace('\\', '').lower())
            except Exception as e:
                logger.debug('Error populating disk PNP device cache (non-critical): %s', e)

            self.get_hardware()
            if children:
                for primary in self._ide_results:
                    for element in self.wmi_system.Win32_IDEControllerdevice(['Antecedent', 'Dependent']):
                        ant = element.antecedent.split('=')[1].replace('"', '').replace('\\\\', '\\')
                        dep = element.dependent.split('=')[1].replace('"', '').replace('\\\\', '\\')
                        if ant == primary.pnpdeviceid:
                            self._attach_ide_child(primary, dep)
                        for secondary in primary.children:
                            if ant == secondary.pnpdeviceid:
                                self._attach_ide_child(secondary, dep)
            return self._ide_results
        except (wmi.x_wmi, wmi.x_access_denied, AttributeError, KeyError, TypeError) as e:
            logger.error(f'Critical error getting IDE hardware data: {e}')
            return []

    def _attach_ide_child(self, parent: Hardware, pnp_id: str):
        wql = self.build_wql_select('Win32_PNPEntity', f'PNPDeviceID="{self._sanitize_wql_value(pnp_id)}"')
        for item in self.wmi_system.query(wql):
            try:
                is_disk = False
                if item.PNPDeviceID and item.PNPDeviceID.strip().replace('\\', '').lower() in self._cached_disk_pnp_ids:
                    is_disk = True

                if not is_disk:
                    try:
                        self._validate_entity('Win32_diskdrive')
                        wql_test = f'SELECT PNPDeviceID FROM Win32_diskdrive WHERE PNPDeviceID="{self._sanitize_wql_value(item.PNPDeviceID)}"'
                        if len(self.wmi_system.query(wql_test)) != 0:
                            is_disk = True
                    except Exception as e:
                        logger.debug('Error checking disk PNP device (non-critical): %s', e)

                if is_disk:
                    disk = self.factory('PhysicalDisk')(item.PNPDeviceID).format_data(children=True)
                else:
                    disk = self.factory('CdRom')(item.PNPDeviceID).format_data(children=True)
                if disk:
                    parent.children.append(disk[0])
            except Exception as e:
                logger.warning(f'Could not attach child {pnp_id} to Ide component: {e}')
