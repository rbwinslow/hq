from ..soup_util import object_is_root, object_is_tag, root_tag_from_soup


class NameTest:
    def __init__(self, value):
        self.value = value.lower()

    def apply(self, axis, node, document):
        return getattr(self, 'apply_to_{0}'.format(axis.name))(node, document)

    def apply_to_ancestor(self, node, document):
        result = []
        while object_is_tag(node):
            if node.parent is None:
                break
            node = node.parent
            if node.name.lower() == self.value:
                result.append(node)
        return result

    def apply_to_child(self, node, document):
        result = []
        if object_is_root(node):
            root_tag = root_tag_from_soup(node)
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
