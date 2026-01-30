# Copyright (c) 2026 Jose Antonio Chavarría <jachavar@gmail.com>
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

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Hardware:
    id: str = 'unknown'
    class_: str = 'unknown'  # 'class' is a reserved keyword
    claimed: bool = False
    handle: str = ''
    description: str = ''
    product: str = 'Error getting data'
    vendor: str = 'Error getting data'
    physid: str = '0'
    serial: str = 'Error getting data'
    children: List['Hardware'] = field(default_factory=list)

    # Optional fields for specific hardware types
    width: int = 0
    size: int = 0
    clock: int = 0
    capacity: int = 0
    units: str = ''
    date: str = ''
    version: str = ''
    logicalname: str = ''
    dev: str = ''
    businfo: str = ''
    slot: str = ''
    deviceid: str = ''
    pnpdeviceid: str = ''
    parent_pnpdeviceid: str = ''
    configuration: Dict[str, str] = field(default_factory=dict)
    capabilities: Dict[str, str] = field(default_factory=dict)

    def to_dict(self):
        """
        Convert to dictionary, handling the 'class_' field renaming.
        """
        data = {
            'id': self.id,
            'class': self.class_,
            'claimed': self.claimed,
            'handle': self.handle,
            'description': self.description,
            'product': self.product,
            'vendor': self.vendor,
            'physid': self.physid,
            'serial': self.serial,
            'children': [child.to_dict() for child in self.children],
        }

        if self.width:
            data['width'] = self.width
        if self.size:
            data['size'] = self.size
        if self.clock:
            data['clock'] = self.clock
        if self.capacity:
            data['capacity'] = self.capacity
        if self.units:
            data['units'] = self.units
        if self.date:
            data['date'] = self.date
        if self.version:
            data['version'] = self.version
        if self.logicalname:
            data['logicalname'] = self.logicalname
        if self.dev:
            data['dev'] = self.dev
        if self.businfo:
            data['businfo'] = self.businfo
        if self.slot:
            data['slot'] = self.slot
        if self.deviceid:
            data['deviceid'] = self.deviceid
        if self.pnpdeviceid:
            data['pnpdeviceid'] = self.pnpdeviceid
        if self.parent_pnpdeviceid:
            data['parent_pnpdeviceid'] = self.parent_pnpdeviceid
        if self.configuration:
            data['configuration'] = self.configuration
        if self.capabilities:
            data['capabilities'] = self.capabilities

        return data
