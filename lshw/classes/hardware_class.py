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

import wmi


class HardwareClass():
    """
    Interface class
    Abstract methods
    """

    __DESC__ = 'Unknown'
    __ERROR__ = 'Error getting data'

    # http://stackoverflow.com/questions/3786762/dynamic-base-class-and-factories
    _entity_ = None
    _entities_ = {}

    @classmethod
    def factory(cls, entity):
        return cls._entities_[entity]

    @classmethod
    def register(cls, entity):
        def decorator(subclass):
            cls._entities_[entity] = subclass
            subclass._entity_ = entity

            return subclass

        return decorator

    def __init__(self):
        self.wmi_system = wmi.WMI()
        self.wmi_method = None

        self.formatted_data = {}

        self.properties_to_get = []
        self.properties_to_return = {}

        self.hardware_set = []
        self.hardware_set_to_return = []

    def _update_properties_to_return(self):
        self.properties_to_return = {
            el: self.__DESC__ for el in self.properties_to_get
        }

    def check_values(self):
        for hw_item in self.hardware_set:
            for prop in self.properties_to_return:
                try:
                    self.properties_to_return[prop] = getattr(hw_item, prop)
                except AttributeError:
                    self.properties_to_return[prop] = self.__DESC__

            self.hardware_set_to_return.append(
                self.properties_to_return.copy()
            )

    def get_hardware(self):
        if self.wmi_method:
            for element in getattr(self.wmi_system, self.wmi_method)(
                self.properties_to_get
            ):
                self.hardware_set.append(element)

            self.check_values()
        else:
            raise NotImplementedError

    def format_data(self, children=False):
        raise NotImplementedError
