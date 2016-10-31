
from enum import Enum


class Axis(Enum):
    # standard
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
    # extended
    css_class           = 13


    def is_reverse_order(self):
        return self in reverse_order_axes

    def token(self):
        return self.name.replace('_', '-')

    @classmethod
    def abbreviations(self):
        return _abbreviations.keys()

    @classmethod
    def canonicalize(cls, name):
        if name in _abbreviations.keys():
            result = _abbreviations[name]
        else:
            result = name.replace('-', '_')
        return result


_abbreviations = {
    '^': 'ancestor',
    '^^': 'ancestor_or_self',
    '@': 'attribute',
    '.': 'css_class',
    'class': 'css_class',
    '~': 'descendant',
    '>>': 'following',
    '>': 'following_sibling',
    '<<': 'preceding',
    '<': 'preceding_sibling',
}


reverse_order_axes = {Axis.ancestor, Axis.ancestor_or_self, Axis.preceding, Axis.preceding_sibling}
