from hq.hquery.axis import Axis
from hq.hquery.syntax_error import HquerySyntaxError
from hq.soup_util import debug_dump_node, soup_from_any_tag, debug_dump_long_string
from hq.verbosity import verbose_print
from hq.hquery.expression_context import get_context_node, peek_context
from hq.hquery.evaluation_in_context import evaluate_across_contexts, evaluate_in_context
from hq.hquery.functions.core_number import number
from hq.hquery.object_type import is_number
from hq.hquery.sequences import make_node_set


class LocationPath:

    def __init__(self, first_axis, first_node_test, first_predicates, absolute=False, root_expression=None):
        self.absolute = absolute
        self.root_expression = root_expression
        self.steps = []
        self.append_step(first_axis, first_node_test, first_predicates)
        if self.absolute and self.root_expression is not None:
            raise HquerySyntaxError('internal error forming location path; it looks both rooted and absolute')


    def __len__(self):
        return len(self.steps)


    def __str__(self):
        return '{0}{1}{2}'.format('' if self.root_expression is None else '<expr>/',
                                  '/' if self.absolute else '',
                                  '/'.join([str(step) for step in self.steps]))


    def append_step(self, axis, node_test, predicates):
        if axis == Axis.css_class and not node_test.is_name_test:
            raise HquerySyntaxError('CSS class axis must be followed by a name test, not a node test')
        self.steps.append(LocationPathStep(axis, node_test, predicates))


    def debug_dump(self):
        return debug_dump_long_string(str(self))


    def evaluate(self):
        verbose_print(lambda: 'Evaluating location path {0}'.format(self.debug_dump()), indent_after=True)

        if self.absolute:
            verbose_print('Switching context to root because this path is absolute.')
            results = evaluate_in_context(soup_from_any_tag(get_context_node()),
                                          lambda: self._evaluate_steps(self.steps))
        elif self.root_expression is not None:
            results = evaluate_across_contexts(self.root_expression(), lambda: self._evaluate_steps(self.steps))
        else:
            results = self._evaluate_steps(self.steps)

        verbose_print('Evaluation completed; location path selected {0} nodes'.format(len(results)),
                      outdent_before=True)
        return make_node_set(results, reverse=False)


    def _evaluate_steps(self, remaining_steps):
        step = remaining_steps[0]
        verbose_print(lambda: 'Evaluating step {0}'.format(remaining_steps[0]), indent_after=True)

        result_set = make_node_set(step.node_test.apply(step.axis, get_context_node()),
                                   reverse=step.axis.is_reverse_order())
        verbose_print(lambda: 'Axis and node test produced {0} matching nodes'.format(len(result_set)))

        for index, expression_fn in enumerate(step.predicates):
            def accept_context_node():
                context = peek_context()

                format_str = u'Evaluating predicate expression for context node at position {0} of {1}: {2}.'
                verbose_print(lambda: format_str.format(context.position, context.size, debug_dump_node(context.node)))

                value = expression_fn()
                if is_number(value):
                    accept = number(context.position) == value
                else:
                    accept = bool(value)

                verbose_print(lambda: u'{0} node {1}'.format('Accepted' if accept else 'Rejected',
                                                             debug_dump_node(context.node)))
                return [context.node] if accept else []

            verbose_print(lambda: 'Evaluating predicate #{0} against {1} nodes'.format(index + 1, len(result_set)),
                          indent_after=True)
            result_set = evaluate_across_contexts(result_set, accept_context_node)
            verbose_print(
                lambda: 'Evaluation of predicate #{0} complete; accepted {1} nodes.'.format(index + 1, len(result_set)),
                outdent_before=True)

        if len(remaining_steps) > 1:
            result_set = evaluate_across_contexts(result_set, lambda: self._evaluate_steps(remaining_steps[1:]))

        verbose_print(lambda: 'Step evaluation completed; returning {0} nodes.'.format(len(result_set)),
                      outdent_before=True)
        return result_set



class LocationPathStep:

    def __init__(self, axis, node_test, predicates):
        self.axis = axis
        self.node_test = node_test
        self.predicates = predicates

    def __str__(self):
        return '{0}::{1}{2}'.format(self.axis.name, repr(self.node_test), '[predicate]' * len(self.predicates))
