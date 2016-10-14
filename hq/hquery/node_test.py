from hq.hquery.axis import Axis

from ..soup_util import is_root_node, is_tag_node, is_text_node, AttributeNode, is_attribute_node, is_any_node, root_tag_from_soup, \
    is_comment_node


def _accept_principal_node_type(node, axis=None):
    return is_attribute_node(node) if axis == Axis.attribute else is_tag_node(node)


def _make_axis_agnostic_accept_fn(fn):
    def evaluate(node, axis=None):
        return fn(node)
    return evaluate


def _make_name_accept_fn(value):
    def evaluate(node, axis=None):
        if axis == Axis.css_class:
            return is_tag_node(node) and 'class' in node.attrs and value in node['class']
        else:
            type_fn = is_attribute_node if axis == Axis.attribute else is_tag_node
            return type_fn(node) and node.name.lower() == value
    return evaluate


class NodeTest:

    def __init__(self, value, name_test=False):
        value = value.lower()
        self.repr = value
        self.is_name_test = name_test

        if name_test:
            self.accept_fn = _make_name_accept_fn(value)
        elif value == '*':
            self.accept_fn = _accept_principal_node_type
        elif value == 'node':
            self.accept_fn = _make_axis_agnostic_accept_fn(is_any_node)
        elif value == 'text':
            self.accept_fn = _make_axis_agnostic_accept_fn(is_text_node)
        elif value == 'comment':
            self.accept_fn = _make_axis_agnostic_accept_fn(is_comment_node)

        self.repr = '{0}{1}'.format(self.repr, '' if name_test or value == '*' else '()')


    def __repr__(self):
        return self.repr


    def apply(self, axis, node):
        nodes = getattr(self, 'gather_{0}'.format(axis.name))(node)
        return [node for node in nodes if self.accept_fn(node, axis=axis)]


    def gather_ancestor(self, node):
        if hasattr(node, 'parents'):
            return list(node.parents)
        else:
            return []


    def gather_ancestor_or_self(self, node):
        result = self.gather_self(node)
        result.extend(self.gather_ancestor(node))
        return result


    def gather_attribute(self, node):
        return list(AttributeNode.enumerate(node))


    def gather_child(self, node):
        if is_root_node(node):
            return [root_tag_from_soup(node)]
        elif is_tag_node(node):
            return node.contents
        else:
            return []


    def gather_css_class(self, node):
        return self.gather_child(node)


    def gather_descendant(self, node):
        if hasattr(node, 'descendants'):
            return list(node.descendants)
        else:
            return []


    def gather_descendant_or_self(self, node):
        result = self.gather_self(node)
        result.extend(self.gather_descendant(node))
        return result


    def gather_following(self, node):
        result = []
        while is_tag_node(node):
            for sibling in node.next_siblings:
                result.append(sibling)
                result.extend(self.gather_descendant(sibling))
            node = node.parent
        return result


    def gather_following_sibling(self, node):
        if hasattr(node, 'next_siblings'):
            return list(node.next_siblings)
        else:
            return []


    def gather_parent(self, node):
        if hasattr(node, 'parent') and node.parent is not None:
            return [node.parent]
        else:
            return []


    def gather_preceding(self, node):
        result = []
        while is_tag_node(node):
            for sibling in node.previous_siblings:
                result.append(sibling)
                result.extend(self.gather_descendant(sibling))
            node = node.parent
        return result


    def gather_preceding_sibling(self, node):
        if hasattr(node, 'previous_siblings'):
            return list(node.previous_siblings)
        else:
            return []


    def gather_self(self, node):
        return [node]
