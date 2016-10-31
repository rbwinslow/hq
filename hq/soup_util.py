import re
from builtins import str
from bs4 import BeautifulSoup

from .string_util import truncate_string
from .verbosity import verbose_print


class AttributeNode:

    def __init__(self, name, value):
        self.name = name
        self.value = ' '.join(value) if isinstance(value, list) else value

    def __repr__(self):
        return 'AttributeNode("{0}", "{1}")'.format(self.name, self.value)

    @classmethod
    def enumerate(cls, node):
        if hasattr(node, 'hq_attrs') and _isnt_root_with_odd_ghost_hq_attrs_on_it_for_reasons_i_dont_understand(node):
            return node.hq_attrs
        else:
            return []


def debug_dump_long_string(s, length=50, one_line=True, suffix='...'):
    return truncate_string(s, length, one_line, suffix)


def debug_dump_node(obj):
    if is_root_node(obj):
        return 'ROOT DOCUMENT'
    elif is_tag_node(obj):
        return u'ELEMENT {0}'.format(debug_dump_long_string(str(obj)))
    elif is_attribute_node(obj):
        return 'ATTRIBUTE {0}="{1}"'.format(obj.name, debug_dump_long_string(obj.value))
    elif is_text_node(obj):
        return u'TEXT "{0}"'.format(debug_dump_long_string(obj.string))
    elif is_comment_node(obj):
        return u'COMMENT "{0}"'.format(debug_dump_long_string(obj.string))
    else:
        return 'NODE type {0}'.format(obj.__class__.__name__)


def derive_text_from_node(obj, preserve_space=False):
    if is_tag_node(obj) or is_root_node(obj):
        result = u''
        strings = list(obj.strings)
        cursor = 0
        for run in (strings if preserve_space else obj.stripped_strings):
            if preserve_space:
                add_space = False
            else:
                while cursor < len(strings):
                    if run in strings[cursor]:
                        break
                    else:
                        cursor += 1
                if cursor < len(strings):
                    add_space = strings[cursor][0].isspace() or (cursor > 0 and strings[cursor - 1][-1].isspace())
                else:
                    add_space = False
            result += u'{0}{1}'.format(' ' if add_space else '', run)
    elif is_attribute_node(obj):
        result = obj.value
    elif is_text_node(obj):
        result = str(obj)
    else:
        raise RuntimeError("don't know how to derive test from {0}".format(debug_dump_node(obj)))

    if not preserve_space:
        result = re.sub(u'\u00a0', ' ', result)
        result = re.sub(r'\s+', ' ', result).strip()

    return result


def is_any_node(obj):
    return is_root_node(obj) or is_tag_node(obj) or is_attribute_node(obj) or is_text_node(obj) or is_comment_node(obj)


def is_attribute_node(obj):
    return isinstance(obj, AttributeNode)


def is_comment_node(obj):
    return obj.__class__.__name__ == 'Comment'


def is_root_node(obj):
    return obj.__class__.__name__ == 'BeautifulSoup'


def is_tag_node(obj):
    return obj.__class__.__name__ == 'Tag'


def is_text_node(obj):
    return obj.__class__.__name__ == 'NavigableString'


def make_soup(source):
    soup = BeautifulSoup(source, 'html.parser')
    counter = [0]

    def visit_node(node):
        node.hq_doc_index = counter[0]
        counter[0] += 1
        if is_tag_node(node):
            attr_names = sorted(node.attrs.keys(), key=lambda name: name.lower())
            node.hq_attrs = [AttributeNode(name, node.attrs[name]) for name in attr_names]
            for attr in node.hq_attrs:
                visit_node(attr)

    preorder_traverse_node_tree(soup, visit_node, filter=is_any_node)
    verbose_print('Loaded HTML document containing {0} indexed nodes.'.format(counter[0]))
    return soup


def preorder_traverse_node_tree(node, fn, filter=lambda n: is_tag_node(n) or is_root_node(n)):
    if filter(node):
        fn(node)
        if hasattr(node, 'hq_attrs') and _isnt_root_with_odd_ghost_hq_attrs_on_it_for_reasons_i_dont_understand(node):
            for attr in node.hq_attrs:
                preorder_traverse_node_tree(attr, fn, filter)
        if hasattr(node, 'children'):
            for child in node.children:
                preorder_traverse_node_tree(child, fn, filter)


def root_tag_from_any_tag(obj):
    return root_tag_from_soup(soup_from_any_tag(obj))


def root_tag_from_soup(soup):
    return next(tag for tag in soup.children if is_tag_node(tag))


def soup_from_any_tag(obj):
    while obj.parent is not None:
        obj = obj.parent
    return obj


def _isnt_root_with_odd_ghost_hq_attrs_on_it_for_reasons_i_dont_understand(node):
    return node.hq_attrs is not None
