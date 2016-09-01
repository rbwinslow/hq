from hq.verbosity import verbose_print
from hq.xpath.axis import Axis

from ..soup_util import is_root_node, is_tag_node, is_text_node, AttributeNode, is_attribute_node, debug_dump_node


def _accept_name(value):
    def evaluate(node, axis=None):
        type_fn = is_attribute_node if axis == Axis.attribute else is_tag_node
        return type_fn(node) and node.name.lower() == value
    return evaluate


def _accept_any(node, axis=None):
    return is_attribute_node(node) if axis == Axis.attribute else is_tag_node(node)


class NodeTest:
    def __init__(self, value, name_test=False):
        value = value.lower()
        if name_test:
            self.accept_fn = _accept_name(value)
        elif value == 'node' or value == '*':
            self.accept_fn = _accept_any
        elif value == 'text':
            self.accept_fn = is_text_node


    def apply(self, axis, node):
        return getattr(self, 'apply_to_{0}'.format(axis.name))(node)


    def apply_to_ancestor(self, node):
        result = []
        while node.parent is not None:
            node = node.parent
            if self.accept_fn(node):
                result.append(node)
        return result


    def apply_to_attribute(self, node):
        result = []
        if hasattr(node, 'attrs'):
            for attr in AttributeNode.enumerate(node):
                if self.accept_fn(attr, axis=Axis.attribute):
                    result.append(attr)
        return sorted(result, key=lambda attr: attr.name.lower())


    def apply_to_child(self, node):
        result = []
        if is_root_node(node):
            try:
                result.append(next(child for child in node.children if self.accept_fn(child)))
            except StopIteration:
                pass
        elif is_tag_node(node):
            result.extend(child for child in node.children if self.accept_fn(child))
        return result


    def apply_to_descendant(self, node):
        result = []
        if is_tag_node(node) or is_root_node(node):
            result = [tag for tag in node.descendants if self.accept_fn(tag)]
        return result


    def apply_to_following(self, node):
        result = []
        while is_tag_node(node):
            while hasattr(node, 'next_sibling') and node.next_sibling is not None:
                node = node.next_sibling
                if self.accept_fn(node):
                    result.append(node)
                result.extend(self.apply_to_descendant(node))
            node = node.parent
        return result


    def apply_to_following_sibling(self, node):
        result = []
        while hasattr(node, 'next_sibling') and node.next_sibling is not None:
            node = node.next_sibling
            if self.accept_fn(node):
                result.append(node)
        return result


    def apply_to_parent(self, node):
        result = []
        if self.accept_fn(node.parent):
            result.append(node.parent)
        return result


    def apply_to_preceding(self, node):
        result = []
        while is_tag_node(node):
            while hasattr(node, 'previous_sibling') and node.previous_sibling is not None:
                node = node.previous_sibling
                if self.accept_fn(node):
                    result.append(node)
                descendant_query = self.apply_to_descendant(node)
                descendant_query.reverse()
                result.extend(descendant_query)
            node = node.parent
        result.reverse()
        return result


    def apply_to_preceding_sibling(self, node):
        result = []
        while hasattr(node, 'previous_sibling') and node.previous_sibling is not None:
            node = node.previous_sibling
            if self.accept_fn(node):
                result.append(node)
        result.reverse()
        return result
