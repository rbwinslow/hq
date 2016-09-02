
class ExpressionContext:
    def __init__(self, node):
        self.node = node
        ## Coming soon:
        # self.position = position
        # self.size = size

    def __str__(self):
        return 'context(node={0})'.format(str(self.node))
