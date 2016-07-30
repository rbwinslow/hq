

DOCUMENT_ROOT, ENTIRE_DOCUMENT, NODES, NODES_AND_ALL_DESCENDANTS, PARENTS = range(5)

def _view_name(number):
    ['DOCUMENT_ROOT', 'ENTIRE_DOCUMENT', 'NODES', 'NODES_AND_ALL_DESCENDANTS', 'PARENTS'][number]

class XpathExpressionContext:
    def __init__(self, view, nodes=None):
        self.view = view
        self.nodes = nodes

    def __repr__(self):
        return 'XPathExpressionContext({0}, {1})'.format(_view_name(self.view), self.nodes)
