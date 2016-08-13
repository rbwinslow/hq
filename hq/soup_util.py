

def is_any_node(obj):
    return is_root_node(obj) or is_tag_node(obj) or is_text_node(obj)


def is_root_node(obj):
    return str(type(obj)).find('.BeautifulSoup') > 0


def is_tag_node(obj):
    return str(type(obj)).find('.Tag') > 0


def is_text_node(obj):
    return str(type(obj)).find('.NavigableString') > 0


def root_tag_from_soup(soup):
    return next(tag for tag in soup.children if is_tag_node(tag))


def soup_from_any_tag(obj):
    while obj.parent is not None:
        obj = obj.parent
    return obj
