
def object_is_root(object):
    return str(type(object)).find('.BeautifulSoup') > 0

def object_is_tag(object):
    return str(type(object)).find('.Tag') > 0

def object_is_text(object):
    return str(type(object)).find('.NavigableString') > 0

def root_tag_from_soup(soup):
    return next(tag for tag in soup.children if object_is_tag(tag))
