from hq.xpath.object_type import is_node_set


class XpathQueryError(RuntimeError):

    @classmethod
    def must_be_node_set(cls, presumed_node_set):
        if not is_node_set(presumed_node_set):
            raise XpathQueryError('Expected a node set, but found a(n) {0}'.format(presumed_node_set.__class__.__name__))
