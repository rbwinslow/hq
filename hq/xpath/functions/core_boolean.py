from math import isnan

from hq.xpath.object_type import is_node_set, is_number


exports = ['boolean']


class boolean:

    def __init__(self, obj):
        if is_node_set(obj):
            self.value = len(obj) > 0
        elif is_number(obj):
            self.value = bool(obj) and not isnan(obj)
        else:
            self.value = bool(obj)

    def __bool__(self):
        return self.value

    def __nonzero__(self):
        return self.__bool__()

    def __str__(self):
        return str(self.value).lower()
