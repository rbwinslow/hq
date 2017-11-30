from hq.hquery.object_type import debug_dump_anything
from hq.hquery.sequences import make_sequence, sequence_concat
from hq.hquery.syntax_error import HquerySyntaxError
from hq.hquery.variables import push_variable, variable_scope
from hq.soup_util import debug_dump_long_string
from hq.verbosity import verbose_print


class Flwor:

    def __init__(self):
        self.global_variables = []
        self.per_iteration_variables = []
        self.return_expression = None
        self.sequence_expression = None
        self.sequence_variable = None


    def __str__(self):
        return '{0}{1}return <expr>'.format(
            '' if self.sequence_expression is None else 'for ${0}:=<expr> '.format(self.sequence_variable),
            (' '.join('let ${0} := <expr>'.format(v[0]) for v in self.per_iteration_variables) + ' ') if len(self.per_iteration_variables) else ''
        )


    def append_let(self, variable_name, expression_fn):
        var_tuple = (variable_name, expression_fn)
        if self.sequence_expression is None:
            self.global_variables.append(var_tuple)
        else:
            self.per_iteration_variables.append(var_tuple)


    def debug_dump(self):
        return debug_dump_long_string(str(self))


    def evaluate(self):
        verbose_print('Evaluating FLWOR {0}'.format(self), indent_after=True)

        if self.sequence_expression is not None:
            result = self._evaluate_iteration()
        else:
            result = self._evaluate_without_iteration()

        verbose_print(lambda: 'FLWOR evaluation completed; returning {0}'.format(debug_dump_anything(result)),
                      outdent_before=True)
        return result


    def set_iteration_expression(self, variable_name, expression_fn):
        if self.sequence_expression is not None:
            raise HquerySyntaxError('More than one "for" clause found in FLWOR "{0}"'.format(self.debug_dump()))
        self.sequence_variable = variable_name
        self.sequence_expression = expression_fn


    def set_return_expression(self, expression_fn):
        if self.return_expression is not None:
            raise HquerySyntaxError('More than one return clause found for FLWOR {0}'.format(self.debug_dump()))
        self.return_expression = expression_fn


    def _evaluate_iteration(self):
        with variable_scope():
            self._push_global_variables()

            sequence = make_sequence(self.sequence_expression())
            verbose_print('Iterating over sequence containing {0} items'.format(len(sequence)))
            result = []

            for item in sequence:
                verbose_print(lambda: u'Visiting item {0}'.format(debug_dump_anything(item)), indent_after=True)

                with variable_scope():
                    push_variable(self.sequence_variable, make_sequence(item))
                    self._push_iteration_variables()
                    this_result = make_sequence(self.return_expression())
                    verbose_print('Return clause yielded {0} results for this visit'.format(len(this_result)))
                    result = sequence_concat(result, this_result)

                verbose_print('Visit finished', outdent_before=True)

        return result


    def _evaluate_without_iteration(self):
        with variable_scope():
            self._push_global_variables()
            verbose_print('Evaluating return expression.', indent_after=True)
            result = self.return_expression()
            verbose_print('Return expression produced {0}'.format(str(result)), outdent_before=True)
        return result


    def _push_global_variables(self):
        for let in self.global_variables:
            verbose_print('Evaluating let {0} := <expr>'.format(let[0]))
            push_variable(let[0], let[1]())


    def _push_iteration_variables(self):
        for let in self.per_iteration_variables:
            verbose_print('Evaluating let {0} := <expr>'.format(let[0]))
            push_variable(let[0], let[1]())
