from hq.hquery.variables import push_variable
from hq.verbosity import verbose_print


class Flwor:

    def __init__(self):
        self.lets = []
        self.return_expression = None


    def __str__(self):
        return '{0} return <expr>'.format(' '.join('let ${0} := <expr>'.format(v[0]) for v in self.lets))


    def append_let(self, variable_name, expression_fn):
        self.lets.append((variable_name, expression_fn))


    def evaluate(self):
        verbose_print('Evaluating FLWOR {0}'.format(self), indent_after=True)
        for let in self.lets:
            verbose_print('Evaluating let {0} := <expr>'.format(let[0]))
            push_variable(let[0], let[1]())
        verbose_print('Evaluating return expression.')
        result = self.return_expression()
        verbose_print('FLWOR evaluation completed; returning {0}'.format(result), outdent_before=True)
        return result
