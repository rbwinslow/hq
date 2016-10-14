from builtins import str

from .hquery.object_type import is_sequence
from .soup_util import is_text_node, is_attribute_node, is_comment_node, is_tag_node, derive_text_from_node, \
    is_root_node


def convert_results_to_output_text(results, pretty=True, preserve_space=False):
    if is_sequence(results):
        return '\n'.join(value_object_to_text(object, pretty, preserve_space) for object in results)
    else:
        return value_object_to_text(results, pretty, preserve_space)


def value_object_to_text(obj, pretty, preserve_space):
    if is_comment_node(obj):
        return u'<!-- {0} -->'.format(str(obj).strip())
    elif is_tag_node(obj) or is_root_node(obj):
        return obj.prettify().rstrip(' \t\n') if pretty else str(obj)
    elif is_attribute_node(obj):
        return u'{0}="{1}"'.format(obj.name, derive_text_from_node(obj, preserve_space=preserve_space))
    elif is_text_node(obj):
        return derive_text_from_node(obj, preserve_space=preserve_space)
    else:
        return str(obj)
