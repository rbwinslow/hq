from hq.soup_util import root_tag_from_any_tag, debug_dump_node, soup_from_any_tag
from hq.verbosity import verbose_print
from hq.xpath.expression_context import get_context_node, evaluate_across_contexts, peek_context, evaluate_in_context
from hq.xpath.functions.core_number import number
from hq.xpath.object_type import make_node_set, is_number


class LocationPath:

    def __init__(self, first_axis, first_node_test, first_predicates, absolute=False):
        self.absolute = absolute
        self.steps = []
        self.append_step(first_axis, first_node_test, first_predicates)


    def __len__(self):
        return len(self.steps)


    def __str__(self):
        return '{0}{1}'.format('/' if self.absolute else '', '/'.join([str(step) for step in self.steps]))


    def append_step(self, axis, node_test, predicates):
        self.steps.append(LocationPathStep(axis, node_test, predicates))


    def evaluate(self):
        verbose_print('Evaluating location path with {0} steps'.format(len(self)), indent_after=True)

        if self.absolute:
            verbose_print('Switching context to root because this path is absolute.')
            results = evaluate_in_context(soup_from_any_tag(get_context_node()),
                                          lambda: self._evaluate_steps(self.steps))
        else:
            results = self._evaluate_steps(self.steps)

        verbose_print('Evaluation completed; location path selected {0} nodes'.format(len(results)),
                      outdent_before=True)
        return make_node_set(results, reverse=False)


    def _evaluate_steps(self, remaining_steps):
        step = remaining_steps[0]
        start_msg = 'Evaluating step {0}::{1} with {2} predicates'.format(step.axis.name,
                                                                          repr(step.node_test),
                                                                          len(step.predicates))
        verbose_print(start_msg, indent_after=True)

        result_set = make_node_set(step.node_test.apply(step.axis, get_context_node()),
                                   reverse=step.axis.is_reverse_order())
        verbose_print('Initial node set from axis and node test contains {0} nodes'.format(len(result_set)))

        for index, expression_fn in enumerate(step.predicates):
            def accept_context_node():
                context = peek_context()

                format_str = 'Evaluating predicate expression for context node at position {0} of {1}: {2}.'
                verbose_print(format_str.format(context.position, context.size, debug_dump_node(context.node)))

                value = expression_fn()
                if is_number(value):
                    accept = number(context.position) == value
                else:
                    accept = bool(value)

                verbose_print('{0} node {1}'.format('Accepted' if accept else 'Rejected',
                                                    debug_dump_node(context.node)))
                return [context.node] if accept else []

            verbose_print('Evaluating predicate #{0} against {1} nodes'.format(index + 1, len(result_set)),
                          indent_after=True)
            result_set = evaluate_across_contexts(result_set, accept_context_node)
            message = 'Evaluation of predicate #{0} complete; accepted {1} nodes.'.format(index + 1, len(result_set))
            verbose_print(message, outdent_before=True)

        if len(remaining_steps) > 1:
            result_set = evaluate_across_contexts(result_set, lambda: self._evaluate_steps(remaining_steps[1:]))

        verbose_print('Step evaluation completed; returning {0} nodes.'.format(len(result_set)), outdent_before=True)
        return result_set



class LocationPathStep:

    def __init__(self, axis, node_test, predicates):
        self.axis = axis
        self.node_test = node_test
        self.predicates = predicates

    def __str__(self):
        return '{0}::{1}{2}'.format(self.axis.name, repr(self.node_test), '[predicate]' * len(self.predicates))
