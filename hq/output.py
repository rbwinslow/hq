from builtins import str

from .hquery.object_type import is_node_set, is_sequence
from .soup_util import is_text_node, is_attribute_node, is_comment_node, is_any_node


def result_object_to_text(obj, pretty=True):
    if is_sequence(obj):
        return sequence_to_text(obj, pretty)
    else:
        return str(obj)


def value_object_to_text(obj, pretty):
    if is_comment_node(obj):
        return u'<!-- {0} -->'.format(str(obj).strip())
    elif not pretty or is_text_node(obj) or is_attribute_node(obj):
        return str(obj)
    elif is_any_node(obj):
        return obj.prettify().rstrip(' \t\n')
    else:
        return str(obj)


def sequence_to_text(objects, pretty):
    return '\n'.join(value_object_to_text(object, pretty) for object in objects)
