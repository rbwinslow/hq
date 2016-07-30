
from .axis import Axis

class XpathExpressionContext:
    def __init__(self, axis=Axis.child, nodes=None):
        self.axis = axis
        self.nodes = nodes

    def __repr__(self):
        return '{0}::{1}'.format(self.axis.name, self.nodes)
