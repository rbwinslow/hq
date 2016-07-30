
def object_is_root(object):
    return str(type(object)).find('.BeautifulSoup') > 0

def object_is_tag(object):
    return str(type(object)).find('.Tag') > 0
