from hq.hquery.evaluation_error import HqueryEvaluationError
from hq.hquery.object_type import debug_dump_anything
from hq.hquery.sequences import make_sequence, sequence_concat
from hq.hquery.variables import push_variable, variable_scope
from hq.verbosity import verbose_print


class UnionDecomposition:

    def __init__(self):
        self.mapping_generators = None
        self.union_expression = None


    def __str__(self):
        union_str = ' | '.join('<expr>' * len(self.mapping_generators))
        return '{0} => {0}'.format(union_str)


    def evaluate(self):
        verbose_print('Evaluating union decomposition ({} clauses)'.format(len(self.mapping_generators)),
                      indent_after=True)

        sequence = make_sequence(self.union_expression())
        result = []

        for item in sequence:
            verbose_print(lambda: u'Visiting item {0}'.format(debug_dump_anything(item)), indent_after=True)

            with variable_scope():
                push_variable('_', make_sequence(item))
                if not hasattr(item, 'union_index'):
                    raise HqueryEvaluationError(
                        "Union decomposition applied to something that wasn't produced by a union"
                    )
                if item.union_index >= len(self.mapping_generators):
                    raise HqueryEvaluationError("Decomposed union had more clauses than its mapping")
                this_result = make_sequence(self.mapping_generators[item.union_index]())
                verbose_print(
                    'Mapping yielded {0} results for this visit'.format(
                        len(this_result)))
                result = sequence_concat(result, this_result)

            verbose_print('Visit finished', outdent_before=True)

        verbose_print('Union decomposition completed', outdent_before=True)
        return result


    def set_mapping_generators(self, mgs):
        self.mapping_generators = mgs


    def set_union_expression(self, ug):
        self.union_expression = ug
