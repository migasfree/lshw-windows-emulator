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

    def get_hardware(self, children):
        ide_controller_device = {}
        ide_controller_device_set = []

        ide_controller_device_primary = []
        for ide_assoc in self.wmi_system.Win32_IDEControllerdevice(['Antecedent', 'Dependent']):
            ide_controller_device['ant_pref'] = ide_assoc.antecedent.split('=')[0].split(':')[0]
            ide_controller_device['ant_class'] = ide_assoc.antecedent.split('=')[0].split(':')[1]
            ide_controller_device['ant_value'] = (
                ide_assoc.antecedent.split('=')[1].replace('"', '').replace('\\\\', '\\')
            )

            ide_controller_device['dep_pref'] = ide_assoc.dependent.split('=')[0].split(':')[0]
            ide_controller_device['dep_class'] = ide_assoc.dependent.split('=')[0].split(':')[1]
            ide_controller_device['dep_value'] = (
                ide_assoc.dependent.split('=')[1].replace('"', '').replace('\\\\', '\\')
            )

            # get only primary IDE controllers (without duplicates)
            exist = False
            if ide_controller_device['ant_value'][0:4] == 'PCI\\':
                for element in ide_controller_device_primary:
                    if element == ide_controller_device['ant_value']:
                        exist = True

                if exist is False:
                    ide_controller_device_primary.append(ide_controller_device['ant_value'])

            ide_controller_device_set.append(ide_controller_device.copy())

        ret = []
        id_disk = 0
        id_cont_prim = 0
        fields = self.build_wql_fields()
        for element in ide_controller_device_primary:
            wql = f'SELECT {fields} FROM Win32_IDEController WHERE PNPDeviceID="{element}"'
            # for ide in self.wmi_system.Win32_IDEController(self.properties_to_get, PNPDeviceID=element):
            for ide in self.wmi_system.query(wql):
                primary_controller = Hardware(
                    id=f'ide:{id_cont_prim}',
                    class_='',
                    claimed=True,
                    handle='',
                    description=ide.Description,
                    product=ide.Caption,
                    vendor=ide.Manufacturer,
                    physid='',
                    serial='',
                )
                primary_controller.businfo = ''
                primary_controller.logicalname = ''
                primary_controller.version = ''
                primary_controller.width = 0
                primary_controller.clock = 0
                primary_controller.pnpdeviceid = ide.PNPDeviceID

                id_cont_prim += 1

                id_cont_sec = 0
                id_disk = 0
                for element2 in ide_controller_device_set:
                    if element2['ant_value'] == ide.PNPDeviceID:
                        # first, search secondary controllers
                        wql2 = 'SELECT {} FROM Win32_IDEController WHERE PNPDeviceID="{}"'.format(
                            fields, element2['dep_value']
                        )
                        for ide2 in self.wmi_system.query(wql2):
                            secondary_controller = Hardware(
                                id=f'channel:{ide2.PNPDeviceID[-1]}',
                                class_='',
                                claimed=True,
                                handle='',
                                description=ide2.Description,
                                product=ide2.Caption,
                                vendor=ide2.Manufacturer,
                                physid='',
                                serial='',
                            )
                            secondary_controller.businfo = ''
                            secondary_controller.logicalname = ''
                            secondary_controller.version = ''
                            secondary_controller.width = 0
                            secondary_controller.clock = 0
                            secondary_controller.pnpdeviceid = ide2.PNPDeviceID

                            id_cont_sec += 1

                            if children:
                                for element3 in ide_controller_device_set:
                                    if element3['ant_value'] == ide2.PNPDeviceID:
                                        wql3 = 'SELECT {} FROM Win32_PNPEntity WHERE PNPDeviceID="{}"'.format(
                                            fields, element3['dep_value']
                                        )
                                        for ide3 in self.wmi_system.query(wql3):
                                            if len(ide3.associators(wmi_result_class='Win32_DiskDrive')) != 0:
                                                hw_item_set = self.factory('PhysicalDisk')(ide3.PNPDeviceID)
                                            else:
                                                # CD or DVD
                                                hw_item_set = self.factory('CdRom')(ide3.PNPDeviceID)

                                            try:
                                                # returns List[Hardware]
                                                disk = hw_item_set.format_data(children=True)

                                                id_disk += 1
                                                secondary_controller.children.append(disk[0])
                                            except Exception as e:
                                                logger.warning(
                                                    f'Could not get children for secondary controller in Ide: {e}'
                                                )

                            primary_controller.children.append(secondary_controller)

                        if children:
                            wql4 = 'SELECT {} FROM Win32_PNPEntity WHERE PNPDeviceID="{}"'.format(
                                fields, element2['dep_value']
                            )
                            for ide4 in self.wmi_system.query(wql4):
                                try:
                                    if len(ide4.associators(wmi_result_class='Win32_DiskDrive')) != 0:
                                        disk = self.factory('PhysicalDisk')(ide4.PNPDeviceID).format_data(children=True)
                                        id_disk += 1
                                        primary_controller.children.append(disk[0])
                                    elif len(ide4.associators(wmi_result_class='Win32_CDROMDrive')) != 0:
                                        disk = self.factory('CdRom')(ide4.PNPDeviceID).format_data(children=True)
                                        id_disk += 1
                                        primary_controller.children.append(disk[0])
                                except Exception as e:
                                    logger.warning(f'Could not get children for primary controller in Ide: {e}')

                ret.append(primary_controller)

        return ret

    def format_data(self, children=False):
        try:
            return self.get_hardware(children)
        except Exception:
            return []
