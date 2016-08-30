
from enum import Enum


class Axis(Enum):
    child = 1
    descendant = 2
    parent = 3
    ancestor = 4
    following_sibling = 5
    preceding_sibling = 6
    following = 7
    preceding = 8

    def token(self):
        return self.name.replace('_', '-')
