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

from .hardware import Hardware
from .hardware_class import HardwareClass


@HardwareClass.register('UsbDevice', parent='Usb')
class UsbDevice(HardwareClass):
    """
    Gets plugged usb devices information using WMI
    """

    def __init__(self, dev_id=None):
        super().__init__()

        self.dev_id = dev_id if dev_id is not None else []

        self.hardware = Hardware(
            id='',
            class_=self.__ERROR__,
            claimed=True,
            handle='',
            description=self.__ERROR__,
            product='',
            vendor=self.__ERROR__,
            physid='',
            serial='',
        )
        self.hardware.businfo = ''
        self.hardware.dev = ''
        self.hardware.version = ''
        self.hardware.pnpdeviceid = self.__ERROR__
        self.hardware.parent_pnpdeviceid = self.__ERROR__
        self.hardware.deviceid = self.__ERROR__

        self.properties_to_get = [
            'Caption',
            'Description',
            'DeviceID',
            'PNPDeviceID',
            'ClassGuid',
            'Service',
        ]

        self._update_properties_to_return()

        # Add Parent_PNPDeviceID and Parent_DeviceID
        self.properties_to_return.update({'Parent_PNPDeviceID': self.__DESC__})

    def get_hardware(self):
        """
        Get Hardware set
        If self.dev_id exists get hardware for DeviceID
        """
        # Exclude devices by Service or ClassGuid (Language Independent)
        # usbccgp: Composite Device
        # USBSTOR: Mass Storage
        # usbhub: Root Hubs
        excluded_services = {'usbccgp', 'USBSTOR', 'usbhub'}
        # {745a17a0...}: Generic HID Class
        excluded_guids = {'{745a17a0-74d3-11d0-b6fe-00a0c90f57da}'}

        usb_controller_device_set = []
        usb_controller_device_list = []

        for usb_assoc in self.wmi_system.Win32_USBControllerdevice(['Antecedent', 'Dependent']):
            ant_value = usb_assoc.antecedent.split('=')[1].replace('"', '').replace('\\\\', '\\')
            dep_value = usb_assoc.dependent.split('=')[1].replace('"', '').replace('\\\\', '\\')
            usb_controller_device_list.append(ant_value)
            usb_controller_device_set.append({'ant_value': ant_value, 'dep_value': dep_value})

        # remove duplicates
        usb_controller_device_primary = set(usb_controller_device_list)

        # If self.dev_id exist then we find "dev_id" associated only.
        if len(self.dev_id) != 0:
            usb_controller_device_primary = self.dev_id

        for usb_ele in usb_controller_device_primary:
            for element in usb_controller_device_set:
                if element['ant_value'] == usb_ele:
                    wql = self.build_wql_select(
                        'Win32_PNPEntity', f'PNPDeviceID="{self._sanitize_wql_value(element["dep_value"])}"'
                    )
                    for hw_item in self.wmi_system.query(wql):
                        service = getattr(hw_item, 'Service', '')
                        guid = getattr(hw_item, 'ClassGuid', '')

                        if service in excluded_services or guid in excluded_guids:
                            continue

                        props = self.properties_to_return.copy()
                        for prop in props:
                            if prop != 'Parent_PNPDeviceID':
                                props[prop] = getattr(hw_item, prop, self.__DESC__)
                            else:
                                props['Parent_PNPDeviceID'] = element['ant_value']

                        self.hardware_set_to_return.append(props)

    def _populate_hardware(self, item_ret: Hardware, hw_item: dict) -> Hardware:
        usb_id_device = 'usb_device'
        guid = hw_item.get('ClassGuid', '')
        desc = hw_item.get('Description', self.__ERROR__)
        caption = hw_item.get('Caption', '')

        # Use ClassGuid for language-neutral identification
        # Keyboards: {4d36e96b...}
        # Mice: {4d36e96f...}
        # Disks: {4d36e967...}
        # Volumes: {71a27cdd...}
        if guid == '{4d36e96b-e325-11ce-bfc1-08002be10318}':
            usb_id_device = 'usb_teclado'
        elif guid == '{4d36e96f-e325-11ce-bfc1-08002be10318}':
            usb_id_device = 'usb_mouse'
        elif guid == '{4d36e967-e325-11ce-bfc1-08002be10318}':
            usb_id_device = 'usb_disk'
        elif guid == '{71a27cdd-817f-11d0-bec7-08002be2092f}':
            usb_id_device = 'usb_vol'
        elif 'SmartBoard' in caption:
            usb_id_device = 'usb_smartboard_xx44'

        item_ret.id = usb_id_device
        item_ret.class_ = desc
        item_ret.description = desc
        item_ret.vendor = desc
        item_ret.pnpdeviceid = hw_item.get('PNPDeviceID', self.__ERROR__)
        item_ret.parent_pnpdeviceid = hw_item.get('Parent_PNPDeviceID', self.__ERROR__)
        item_ret.deviceid = hw_item.get('DeviceID', self.__ERROR__)
        item_ret.class_guid = guid
        item_ret.service = hw_item.get('Service', '')

        return item_ret
