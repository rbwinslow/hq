from ..soup_util import is_root_node, is_tag_node, root_tag_from_soup


class NameTest:
    def __init__(self, value):
        self.value = value.lower()

    def apply(self, axis, node):
        return getattr(self, 'apply_to_{0}'.format(axis.name))(node)

    def apply_to_ancestor(self, node):
        result = []
        while is_tag_node(node):
            if node.parent is None:
                break
            node = node.parent
            if node.name.lower() == self.value:
                result.append(node)
        return result

    def apply_to_child(self, node):
        result = []
        if is_root_node(node):
            root_tag = root_tag_from_soup(node)
            if root_tag.name.lower() == self.value.lower():
                result.append(root_tag)
        elif is_tag_node(node):
            result.extend([child for child in node.children if is_tag_node(child) and child.name.lower() == self.value])
        return result

    def apply_to_descendant(self, node):
        result = []
        if is_tag_node(node) or is_root_node(node):
            result = node(self.value)
        return result

    def apply_to_parent(self, node):
        result = []
        if is_tag_node(node) and node.parent is not None and node.parent.name.lower() == self.value:
            result.append(node.parent)
        return result
