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
from abc import ABC, abstractmethod
from typing import List

import wmi

from .hardware import Hardware

logger = logging.getLogger(__name__)


class WMIConnection:
    """
    Singleton for WMI connection management.
    """

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = wmi.WMI()
        return cls._instance


class HardwareClass(ABC):
    _WMI_ENTITY_ALLOWLIST = frozenset(
        {
            'Win32_baseboard',
            'Win32_bios',
            'Win32_Bus',
            'Win32_cdromdrive',
            'Win32_CDROMDrive',
            'Win32_computersystem',
            'Win32_Computersystemproduct',
            'Win32_diskdrive',
            'Win32_Diskdrive',
            'Win32_DiskDrive',
            'Win32_DiskDriveToDiskPartition',
            'Win32_diskpartition',
            'Win32_Diskpartition',
            'Win32_IDEController',
            'Win32_IDEControllerdevice',
            'Win32_LogicalDisk',
            'Win32_LogicalDiskToPartition',
            'Win32_NetworkAdapter',
            'Win32_physicalMemory',
            'Win32_PNPEntity',
            'Win32_processor',
            'Win32_SoundDevice',
            'Win32_SystemEnclosure',
            'Win32_USBController',
            'Win32_USBControllerdevice',
            'Win32_videoController',
        }
    )
    """
    Base class for hardware information retrieval via WMI.

    This class provides a factory pattern for creating hardware-specific
    subclasses that query Windows Management Instrumentation (WMI).

    Return Type Convention for format_data():
        - Always returns List[Hardware] for consistency.
          Singleton components will return a list with a single element.

    Subclasses must implement:
        - format_data(children: bool = False) -> List[Hardware]
    """

    __DESC__ = 'Unknown'
    __ERROR__ = 'Error getting data'

    # http://stackoverflow.com/questions/3786762/dynamic-base-class-and-factories
    _entity_ = None
    _entities_ = {}  # noqa: RUF012
    _children_ = {}  # noqa: RUF012

    @classmethod
    def factory(cls, entity):
        return cls._entities_[entity]

    @classmethod
    def get_children(cls, entity):
        """
        Get the list of registered children classes for a given entity.
        """
        return [cls._entities_[child_name] for child_name in cls._children_.get(entity, [])]

    @classmethod
    def register(cls, entity, parent=None):
        def decorator(subclass):
            cls._entities_[entity] = subclass
            subclass._entity_ = entity

            if parent:
                parents = [parent] if isinstance(parent, str) else parent
                for p in parents:
                    if p not in cls._children_:
                        cls._children_[p] = []
                    if entity not in cls._children_[p]:
                        cls._children_[p].append(entity)

            return subclass

        return decorator

    def __init__(self):
        self.wmi_system = WMIConnection.get_instance()
        self.wmi_method = None

        self.hardware: List[Hardware] = []

        self.properties_to_get = []
        self.properties_to_return = {}

        self.hardware_set = []
        self.hardware_set_to_return = []

    def _validate_entity(self, entity):
        """
        Validate that the WMI entity is in the allowlist.

        Args:
            entity: WMI table/class name or method name.

        Raises:
            ValueError: If the entity is not in the allowlist.
        """
        if entity not in self._WMI_ENTITY_ALLOWLIST:
            logger.error(f'Security Alert: Unauthorized WMI entity access attempted: {entity}')
            raise ValueError(f'Unauthorized WMI entity: {entity}')

    def build_wql_fields(self):
        """Build comma-separated list of fields for WQL SELECT statement."""
        return ','.join(self.properties_to_get)

    def build_wql_select(self, table, where_clause=''):
        """
        Build a WQL SELECT statement.

        Args:
            table: WMI table name (e.g., 'Win32_NetworkAdapter')
            where_clause: Optional WHERE clause (without 'WHERE' keyword)

        Returns:
            Complete WQL SELECT statement
        """
        self._validate_entity(table)
        fields = self.build_wql_fields()
        wql = f'SELECT {fields} FROM {table}'
        if where_clause:
            wql += f' WHERE {where_clause}'
        return wql

    def execute_wql_query(self, wql):
        """
        Execute a WQL query and populate hardware_set.

        Args:
            wql: Complete WQL query string
        """
        for element in self.wmi_system.query(wql):
            self.hardware_set.append(element)

    def _update_properties_to_return(self):
        self.properties_to_return = dict.fromkeys(self.properties_to_get, self.__DESC__)

    def check_values(self):
        for hw_item in self.hardware_set:
            for prop in self.properties_to_return:
                try:
                    self.properties_to_return[prop] = getattr(hw_item, prop)
                except AttributeError as e:
                    logger.warning(f'Could not get property {prop} from {hw_item}: {e}')
                    self.properties_to_return[prop] = self.__DESC__

            self.hardware_set_to_return.append(self.properties_to_return.copy())

    def get_hardware(self):
        if self.wmi_method:
            self._validate_entity(self.wmi_method)
            try:
                for element in getattr(self.wmi_system, self.wmi_method)(self.properties_to_get):
                    self.hardware_set.append(element)
            except (wmi.x_wmi, AttributeError) as e:
                logger.error(f'Error getting hardware info for {self._entity_}: {e}')
                return

            self.check_values()
        else:
            raise NotImplementedError

    @abstractmethod
    def format_data(self, children=False):
        """
        Format hardware data for output.

        Args:
            children: If True, include child hardware components in output.

        Returns:
            List[Hardware]: A list of hardware components.
        """
        pass
