from hq.verbosity import verbose_print

from ..soup_util import is_root_node, is_tag_node, is_text_node, AttributeNode, is_attribute_node


class NodeTest:
    def __init__(self, value, name_test=False):
        value = value.lower()
        if name_test:
            self.accept_fn = lambda n: (is_tag_node(n) or is_attribute_node(n)) and (n.name.lower() == value)
        elif value == 'node' or value == '*':
            self.accept_fn = is_tag_node
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
                if self.accept_fn(attr):
                    result.append(attr)
                    break
        return result


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
