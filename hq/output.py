from .xpath.object_type import is_node_set

from .soup_util import is_text_node


def result_object_to_text(obj, pretty=True):
    if is_node_set(obj):
        return soup_objects_to_text(obj, pretty)
    else:
        return str(obj)


def soup_object_to_text(obj, pretty):
    if is_text_node(obj) or not pretty:
        return str(obj)
    else:
        return obj.prettify().rstrip(' \t\n')


def soup_objects_to_text(objects, pretty):
    return '\n'.join(soup_object_to_text(object, pretty) for object in objects)
