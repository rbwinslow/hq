
from .soup_util import is_text_node


def soup_object_to_text(object):
    if is_text_node(object):
        return str(object)
    else:
        return object.prettify().rstrip(' \t\n')

def soup_objects_to_text(objects):
    return '\n'.join(soup_object_to_text(object) for object in objects)
