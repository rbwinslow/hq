from hq.hquery.object_type import make_sequence, sequence_concat, make_node_set
from hq.hquery.variables import push_variable, variable_context
from hq.soup_util import debug_dump_long_string
from hq.verbosity import verbose_print


class Flwor:

    def __init__(self):
        self.lets = []
        self.return_expression = None
        self.sequence_expression = None
        self.sequence_variable = None


    def __str__(self):
        return '{0}{1}return <expr>'.format(
            '' if self.sequence_expression is None else 'for ${0}:=<expr> '.format(self.sequence_variable),
            (' '.join('let ${0} := <expr>'.format(v[0]) for v in self.lets) + ' ') if len(self.lets) else ''
        )


    def append_let(self, variable_name, expression_fn):
        self.lets.append((variable_name, expression_fn))


    def debug_dump(self):
        return debug_dump_long_string(str(self))


    def evaluate(self):
        verbose_print('Evaluating FLWOR {0}'.format(self), indent_after=True)

        if self.sequence_expression is not None:
            sequence = make_sequence(self.sequence_expression())
            result = []
            verbose_print('Iterating over sequence containing {0} items'.format(len(sequence)))
            for item in sequence:
                verbose_print('Visiting item {0}'.format(debug_dump_long_string(str(item))), indent_after=True)
                with variable_context():
                    push_variable(self.sequence_variable, make_sequence(item))
                    self._push_variables()
                    this_result = make_sequence(self.return_expression())
                    verbose_print('Return clause yielded {0} reults for this visit'.format(len(this_result)))
                    result = sequence_concat(result, this_result)
                verbose_print('Visit finished', outdent_before=True)
        else:
            with variable_context():
                self._push_variables()
                verbose_print('Evaluating return expression.', indent_after=True)
                result = self.return_expression()
                verbose_print('Return expression produced {0}'.format(str(result)), outdent_before=True)

        verbose_print('FLWOR evaluation completed; returning {0}'.format(result), outdent_before=True)
        return result


    def _push_variables(self):
        for let in self.lets:
            verbose_print('Evaluating let {0} := <expr>'.format(let[0]))
            push_variable(let[0], let[1]())
