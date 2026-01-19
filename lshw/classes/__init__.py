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

from .base_board import BaseBoard
from .cd_rom import CdRom
from .computer_system import ComputerSystem
from .firmware import Firmware
from .graphic_card import GraphicCard
from .hardware_class import HardwareClass
from .ide import Ide
from .logical_disk import LogicalDisk
from .network_card import NetworkCard
from .partition_disk import PartitionDisk
from .pci import Pci
from .physical_disk import PhysicalDisk
from .physical_memory import PhysicalMemory
from .processor import Processor
from .sound_device import SoundDevice
from .usb import Usb
from .usb_device import UsbDevice

__all__ = [
    'BaseBoard',
    'CdRom',
    'ComputerSystem',
    'Firmware',
    'GraphicCard',
    'HardwareClass',
    'Ide',
    'LogicalDisk',
    'NetworkCard',
    'PartitionDisk',
    'Pci',
    'PhysicalDisk',
    'PhysicalMemory',
    'Processor',
    'SoundDevice',
    'Usb',
    'UsbDevice',
]
