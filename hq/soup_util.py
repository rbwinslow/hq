from .verbosity import verbose_print


class AttributeNode:

    def __init__(self, name, value):
        self.name = name
        self.value = ' '.join(value) if isinstance(value, list) else value

    def __repr__(self):
        return 'AttributeNode("{0}", "{1}")'.format(self.name, self.value)

    def __str__(self):
        return '{0}="{1}"'.format(self.name, self.value)

    @classmethod
    def enumerate(cls, tag_node):
        if hasattr(tag_node, 'attrs'):
            for name, value in tag_node.attrs.items():
                yield AttributeNode(name, value)


def debug_dump_long_string(s, length=50, one_line=True, suffix='...'):
    if len(s) <= length:
        result = s
    else:
        result = s[:length].rsplit(' ', 1)[0] + suffix
    if one_line:
        result = result.replace('\n', '\\n')
    return result


def debug_dump_node(obj):
    if is_root_node(obj):
        return 'ROOT DOCUMENT'
    elif is_tag_node(obj):
        return 'ELEMENT <{0}>'.format(obj.name)
    elif is_attribute_node(obj):
        return 'ATTRIBUTE {0}="{1}"'.format(obj.name, debug_dump_long_string(obj.value))
    elif is_text_node(obj):
        return 'TEXT "{0}"'.format(debug_dump_long_string(obj.string))
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


def visit_element_and_all_descendants(node, fn):
    if is_root_node(node):
        node = root_tag_from_soup(node)
    if is_tag_node(node):
        for child in node.children:
            visit_element_and_all_descendants(child, fn)
        fn(node)

