
class AttributeNode:

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return 'AttributeNode("{0}", "{1}")'.format(self.name, self.value)

    def __str__(self):
        return '{0}="{1}"'.format(self.name, self.value)

    @classmethod
    def enumerate(cls, tag_node):
        if hasattr(tag_node, 'attrs'):
            for name, value in tag_node.attrs.items():
                yield AttributeNode(name, value)


def debug_dump_node(obj):
    if is_root_node(obj):
        return 'ROOT DOCUMENT'
    elif is_tag_node(obj):
        return 'ELEMENT <{0}>'.format(obj.name)
    elif is_text_node(obj):
        return 'TEXT "{0}"'.format(_debug_dump_long_string(obj.string))
    else:
        return 'NODE type {0}'.format(obj.__class__.__name__)


def is_any_node(obj):
    return is_root_node(obj) or is_tag_node(obj) or is_attribute_node(obj) or is_text_node(obj)


def is_attribute_node(obj):
    return isinstance(obj, AttributeNode)


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


def _debug_dump_long_string(s, length=50, suffix='...'):
    if len(s) <= length:
        return s
    else:
        return s[:length].rsplit(' ', 1)[0] + suffix

