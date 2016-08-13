
class ExpressionContext:
    def __init__(self, node):
        self.node = node
        ## Coming soon:
        # self.position = position
        # self.size = size

    def __repr__(self):
        return 'hq.xpath.ExpressionContext(node={0})'.format(repr(self.node))
