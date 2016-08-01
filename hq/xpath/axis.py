
from enum import Enum


class Axis(Enum):
    child = 1
    descendant = 2
    parent = 3
    ancestor = 4

    def token(self):
        return self.name.replace('_', '-')
