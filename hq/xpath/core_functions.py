from math import isnan
from hq.xpath.object_type import is_node_set, is_number


def boolean(obj):
    if is_node_set(obj):
        return len(obj) > 0
    elif is_number(obj):
        return bool(obj) and not isnan(obj)
    else:
        return bool(obj)
