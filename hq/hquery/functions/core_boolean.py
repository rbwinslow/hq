from math import isnan

from hq.hquery.object_type import is_node_set, is_number, is_boolean


exports = ('boolean', 'false', 'not_', 'true')


class boolean:

    def __init__(self, obj):
        if is_node_set(obj):
            self.value = len(obj) > 0
        elif is_number(obj):
            f = float(obj)
            self.value = bool(f) and not isnan(f)
        else:
            self.value = bool(obj)

    def __bool__(self):
        return self.value

    def __nonzero__(self):
        return self.__bool__()

    def __str__(self):
        return str(self.value).lower()

    def __eq__(self, other):
        return is_boolean(other) and self.value == other.value

    def __repr__(self):
        return 'boolean({0})'.format(self.value)


def false():
    return boolean(False)


def not_(value):
    return boolean(not boolean(value))


def true():
    return boolean(True)
