from hq.hquery.object_type import is_node_set, is_sequence


class HqueryEvaluationError(RuntimeError):

    @classmethod
    def must_be_node_set(cls, obj):
        if not is_node_set(obj):
            raise HqueryEvaluationError('Expected a node set, but found a(n) {0}'.format(obj.__class__.__name__))

    @classmethod
    def must_be_node_set_or_sequence(cls, obj):
        if not (is_node_set(obj) or is_sequence(obj)):
            raise HqueryEvaluationError('Expected a node set or sequence, but found a(n) {0}'.format(
                obj.__class__.__name__
            ))
