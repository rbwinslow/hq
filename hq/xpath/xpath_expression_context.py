

DOCUMENT_ROOT, NODES, NODES_AND_ALL_DESCENDANTS, ENTIRE_DOCUMENT = range(4)


class XpathExpressionContext:
    def __init__(self, view, nodes=None):
        self.view = view
        self.nodes = nodes
