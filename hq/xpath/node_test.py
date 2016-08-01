
from ..soup_util import object_is_root, object_is_tag, object_is_text


class NodeTest:
    def __init__(self, value):
        if value == 'node':
            self.accept_fn = object_is_tag
        elif value == 'text':
            self.accept_fn = object_is_text

    def apply(self, axis, node, document):
        return getattr(self, 'apply_to_{0}'.format(axis.name))(node, document)

    def apply_to_ancestor(self, node, document):
        result = []
        while node.parent is not None:
            node = node.parent
            if self.accept_fn(node):
                result.append(node)
        return result

    def apply_to_child(self, node, document):
        result = []
        if object_is_root(node):
            result.append(next(child for child in node.children if self.accept_fn(child)))
        elif object_is_tag(node):
            result.extend(child for child in node.children if self.accept_fn(child))
        return result

    def apply_to_descendant(self, node, document):
        result = []
        if object_is_tag(node) or object_is_root(node):
            result = [tag for tag in node.descendants if self.accept_fn(tag)]
        return result

    def apply_to_parent(self, node, document):
        result = []
        if self.accept_fn(node.parent):
            result.append(node.parent)
        return result
