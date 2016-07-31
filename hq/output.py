
from .soup_util import object_is_text


def soup_object_to_text(object):
    if object_is_text(object):
        return str(object)
    else:
        return object.prettify().rstrip(' \t\n')

def soup_objects_to_text(objects):
    return '\n'.join(soup_object_to_text(object) for object in objects)
