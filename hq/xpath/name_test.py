from ..soup_util import object_is_root, object_is_tag


class NameTest:
    def __init__(self, value):
        self.value = value.lower()

    def apply(self, axis, node, document):
        return getattr(self, 'apply_to_{0}'.format(axis.snakified()))(node, document)

    def apply_to_child(self, node, document):
        result = []
        if object_is_root(node):
            root_tag = node.contents[0]
            if root_tag.name.lower() == self.value.lower():
                result.append(root_tag)
        elif object_is_tag(node):
            result.extend([child for child in node.children if object_is_tag(child) and child.name.lower() == self.value])
        return result

    def apply_to_descendant(self, node, document):
        result = []
        if object_is_tag(node) or object_is_root(node):
            result = node(self.value)
        return result

    def apply_to_parent(self, node, document):
        result = []
        if object_is_tag(node) and node.parent is not None and node.parent.name.lower() == self.value:
            result.append(node.parent)
        return result
