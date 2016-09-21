
from enum import Enum


class Axis(Enum):
    ancestor            = 1
    ancestor_or_self    = 2
    attribute           = 3
    child               = 4
    descendant          = 5
    descendant_or_self  = 6
    following           = 7
    following_sibling   = 8
    parent              = 9
    preceding           = 10
    preceding_sibling   = 11
    self                = 12

    def is_reverse_order(self):
        return self in (Axis.ancestor, Axis.ancestor_or_self, Axis.preceding, Axis.preceding_sibling)

    def token(self):
        return self.name.replace('_', '-')
