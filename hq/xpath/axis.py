
from enum import Enum


class Axis(Enum):
    child = 1
    descendant = 2
    parent = 3

    def snakified(self):
        return self.name.replace('-', '_')
