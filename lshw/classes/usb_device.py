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

__author__ = [
    'Jose Antonio Chavarría <jachavar@gmail.com>',
    'Alfonso Gómez Sánchez <agomez@zaragoza.es>',
]
__license__ = 'GPLv3'

from copy import deepcopy

from .hardware_class import HardwareClass


@HardwareClass.register('UsbDevice', parent='Usb')
class UsbDevice(HardwareClass):
    """
    Gets plugged usb devices information using WMI
    """

    def __init__(self, dev_id=None):
        super().__init__()

        self.dev_id = dev_id if dev_id is not None else []

        self.formatted_data = {
            'id': '',
            'class': self.__ERROR__,
            'claimed': True,
            'description': self.__ERROR__,
            'vendor': self.__ERROR__,
            'physid': '',
            'businfo': '',
            'dev': '',
            'version': '',
            'serial': '',
            'PNPDeviceID': self.__ERROR__,
            'Parent_PNPDeviceID': self.__ERROR__,
            'DeviceID': self.__ERROR__,
            'children': [],
        }

        self.properties_to_get = [
            'Caption',
            'Description',
            'DeviceID',
            'PNPDeviceID',
        ]

        self._update_properties_to_return()

        # Add Parent_PNPDeviceID and Parent_DeviceID
        self.properties_to_return.update({'Parent_PNPDeviceID': self.__DESC__})

    def get_hardware(self):
        """
        Get Hardware set
        If self.dev_id exists get hardware for DeviceID
        """
        # Devices excluded. We don't need them
        device_excluded = [
            'Dispositivo compuesto USB',
            'Dispositivo de interfaz humana USB',
            'Dispositivo de almacenamiento masivo USB',
            'USB 2.0 Root Hub',
        ]

        usb_controller_device = {}
        usb_controller_device_set = []

        usb_controller_device_list = []
        usb_controller_device_primary = []

        for usb_assoc in self.wmi_system.Win32_USBControllerdevice(['Antecedent', 'Dependent']):
            usb_controller_device['ant_value'] = (
                usb_assoc.antecedent.split('=')[1].replace('"', '').replace('\\\\', '\\')
            )
            usb_controller_device['dep_value'] = (
                usb_assoc.dependent.split('=')[1].replace('"', '').replace('\\\\', '\\')
            )

            # only get USB controllers (without duplicates)
            usb_controller_device_list.append(usb_controller_device['ant_value'])

            usb_controller_device_set.append(usb_controller_device.copy())

        # remove duplicates
        usb_controller_device_primary = set(usb_controller_device_list)

        # If self.dev_id exist then we find "dev_id" associated only.
        if len(self.dev_id) != 0:
            usb_controller_device_primary = self.dev_id

        fields = self.build_wql_fields()
        for usb_ele in usb_controller_device_primary:
            for element in usb_controller_device_set:
                if element['ant_value'] == usb_ele:
                    wql = 'SELECT {} FROM Win32_PNPEntity WHERE PNPDeviceID="{}"'.format(fields, element['dep_value'])
                    for hw_item in self.wmi_system.query(wql):
                        if hw_item.Caption not in device_excluded:
                            for prop in self.properties_to_return:
                                if prop != 'Parent_PNPDeviceID':
                                    try:
                                        self.properties_to_return[prop] = getattr(hw_item, prop)
                                    except AttributeError:
                                        self.properties_to_return[prop] = self.__DESC__
                                else:
                                    self.properties_to_return['Parent_PNPDeviceID'] = element['ant_value']

                            self.hardware_set_to_return.append(self.properties_to_return.copy())

    def format_data(self, children=False):
        self.get_hardware()

        ret = []
        for hw_item in self.hardware_set_to_return:
            usb_id_device = 'usb_device'

            if 'Description' in hw_item:
                if hw_item['Description'] == 'Mouse compatible con HID':
                    usb_id_device = 'usb_mouse'

                if hw_item['Description'] == 'Dispositivo de teclado HID':
                    usb_id_device = 'usb_teclado'

                if hw_item['Description'] == 'SmartBoard XX44':
                    usb_id_device = 'usb_smartboard_xx44'

                if hw_item['Description'] == 'Unidad de disco':
                    usb_id_device = 'usb_disk'

                if hw_item['Description'] == 'Volumen genérico':
                    usb_id_device = 'usb_vol'

            item_ret = deepcopy(self.formatted_data)

            item_ret['id'] = usb_id_device
            item_ret['class'] = hw_item.get('Description', self.__ERROR__)
            item_ret['description'] = hw_item.get('Description', self.__ERROR__)
            item_ret['vendor'] = hw_item.get('Description', self.__ERROR__)
            item_ret['PNPDeviceID'] = hw_item.get('PNPDeviceID', self.__ERROR__)
            item_ret['Parent_PNPDeviceID'] = hw_item.get('Parent_PNPDeviceID', self.__ERROR__)
            item_ret['DeviceID'] = hw_item.get('DeviceID', self.__ERROR__)

            ret.append(item_ret)

        return ret
