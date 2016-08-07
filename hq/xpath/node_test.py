
from ..soup_util import is_root_object, is_tag_object, is_text_object


class NodeTest:
    def __init__(self, value):
        if value == 'node':
            self.accept_fn = is_tag_object
        elif value == 'text':
            self.accept_fn = is_text_object

    def apply(self, axis, node):
        return getattr(self, 'apply_to_{0}'.format(axis.name))(node)

    def apply_to_ancestor(self, node):
        result = []
        while node.parent is not None:
            node = node.parent
            if self.accept_fn(node):
                result.append(node)
        return result

    def apply_to_child(self, node):
        result = []
        if is_root_object(node):
            result.append(next(child for child in node.children if self.accept_fn(child)))
        elif is_tag_object(node):
            result.extend(child for child in node.children if self.accept_fn(child))
        return result

    def apply_to_descendant(self, node):
        result = []
        if is_tag_object(node) or is_root_object(node):
            result = [tag for tag in node.descendants if self.accept_fn(tag)]
        return result

    def apply_to_parent(self, node):
        result = []
        if self.accept_fn(node.parent):
            result.append(node.parent)
        return result
