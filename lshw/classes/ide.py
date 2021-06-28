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

from .hardware_class import HardwareClass
from .physical_disk import PhysicalDisk
from .cd_rom import CdRom


@HardwareClass.register('Ide')
class Ide(HardwareClass):
    """
    Gets the relationship between IDE controllers
    """

    def __init__(self):
        HardwareClass.__init__(self)

        self.formatted_data = {
            "id": "ide:0",
            "class": "",
            "claimed": True,
            "handle": "",
            "description": self.__ERROR__,
            "product": self.__ERROR__,
            "vendor": self.__ERROR__,
            "physid": "",
            "businfo": "",
            "logicalname": [],
            "version": "",
            "width": 0,
            "clock": 0,
            "pnpdeviceid": self.__ERROR__,
            "children": []
        }

        self.properties_to_get = [
            'Manufacturer',
            'Caption',
            'Description',
            'DeviceID',
            'PNPDeviceID'
        ]

        self._update_properties_to_return()

    def get_hardware(self, children):
        ide_controller_device = {}
        ide_controller_device_set = []

        ide_controller_device_primary = []
        for ide_assoc in self.wmi_system.Win32_IDEControllerdevice(
            ["Antecedent", "Dependent"]
        ):
            ide_controller_device['ant_pref'] = ide_assoc.antecedent.split('=')[0].split(':')[0]
            ide_controller_device['ant_class'] = ide_assoc.antecedent.split('=')[0].split(':')[1]
            ide_controller_device['ant_value'] = ide_assoc.antecedent.split('=')[1].replace('"', '').replace('\\\\', '\\')

            ide_controller_device['dep_pref'] = ide_assoc.dependent.split('=')[0].split(':')[0]
            ide_controller_device['dep_class'] = ide_assoc.dependent.split('=')[0].split(':')[1]
            ide_controller_device['dep_value'] = ide_assoc.dependent.split('=')[1].replace('"', '').replace('\\\\', '\\')

            # get only primary IDE controllers (without duplicates)
            exist = False
            if ide_controller_device['ant_value'][0:4] == 'PCI\\':
                for element in ide_controller_device_primary:
                    if element == ide_controller_device['ant_value']:
                        exist = True

                if exist is False:
                    ide_controller_device_primary.append(
                        ide_controller_device['ant_value']
                    )

            ide_controller_device_set.append(ide_controller_device.copy())

        ret = []
        id_disk = 0
        id_cont_prim = 0
        fields = ','.join(self.properties_to_get)
        for element in ide_controller_device_primary:
            wql = 'SELECT {} FROM Win32_IDEController WHERE PNPDeviceID="{}"'.format(
                fields,
                element
            )
            # for ide in self.wmi_system.Win32_IDEController(self.properties_to_get, PNPDeviceID=element):
            for ide in self.wmi_system.query(wql):
                primary_controller = {
                    "id": "ide:{}".format(id_cont_prim),
                    "class": "",
                    "claimed": True,
                    "handle": "",
                    "description": ide.Description,
                    "product": ide.Caption,
                    "vendor": ide.Manufacturer,
                    "physid": "",
                    "businfo": "",
                    "logicalname": "",
                    "version": "",
                    "width": 0,
                    "clock": 0,
                    "pnpdeviceid": ide.PNPDeviceID,
                    "children": []
                }
                id_cont_prim += 1

                id_cont_sec = 0
                id_disk = 0
                for element2 in ide_controller_device_set:
                    if element2['ant_value'] == ide.PNPDeviceID:
                        # first, search secondary controllers
                        wql2 = 'SELECT {} FROM Win32_IDEController WHERE PNPDeviceID="{}"'.format(
                            fields,
                            element2['dep_value']
                        )
                        for ide2 in self.wmi_system.query(wql2):
                            secondary_controller = {
                                "id": "channel:{}".format(ide2.PNPDeviceID[-1]),
                                "class": "",
                                "claimed": True,
                                "handle": "",
                                "description": ide2.Description,
                                "product": ide2.Caption,
                                "vendor": ide2.Manufacturer,
                                "physid": "",
                                "businfo": "",
                                "logicalname": "",
                                "version": "",
                                "width": 0,
                                "clock": 0,
                                "pnpdeviceid": ide2.PNPDeviceID,
                                "children": []
                            }

                            id_cont_sec += 1

                            if children:
                                for element3 in ide_controller_device_set:
                                    if element3['ant_value'] == ide2.PNPDeviceID:
                                        wql3 = 'SELECT {} FROM Win32_PNPEntity WHERE PNPDeviceID="{}"'.format(
                                            fields,
                                            element3['dep_value']
                                        )
                                        for ide3 in self.wmi_system.query(wql3):
                                            if len(ide3.associators(wmi_result_class="Win32_DiskDrive")) != 0:
                                                hw_item_set = PhysicalDisk(ide3.PNPDeviceID)
                                            else:
                                                # CD or DVD
                                                hw_item_set = CdRom(ide3.PNPDeviceID)

                                            Disk = hw_item_set.format_data(children=True)

                                            id_disk += 1
                                            secondary_controller['children'].append(Disk[0])

                            primary_controller['children'].append(
                                secondary_controller
                            )

                        if children:
                            wql4 = 'SELECT {} FROM Win32_PNPEntity WHERE PNPDeviceID="{}"'.format(
                                fields,
                                element2['dep_value']
                            )
                            for ide4 in self.wmi_system.query(wql4):
                                if len(ide4.associators(wmi_result_class="Win32_DiskDrive")) != 0:
                                    disk = PhysicalDisk(ide4.PNPDeviceID).format_data(children=True)
                                    id_disk += 1
                                    primary_controller['children'].append(disk[0])
                                elif len(ide4.associators(wmi_result_class="Win32_CDROMDrive")) != 0:
                                    disk = CdRom(ide4.PNPDeviceID).format_data(children=True)
                                    id_disk += 1
                                    primary_controller['children'].append(disk[0])
                                else:
                                    # only add disks and cdrom drives
                                    pass

                ret.append(primary_controller)

        return ret

    def format_data(self, children=False):
        try:
            return self.get_hardware(children)
        except:
            return self.formatted_data
