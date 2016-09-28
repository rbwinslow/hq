from hq.verbosity import verbose_print

variable_stack = []
NAME, VALUE = range(2)


class variable_context:
    def __enter__(self):
        self.mark = len(variable_stack)

    def __exit__(self, *args):
        del variable_stack[self.mark:]


def push_variable(name, value):
    global variable_stack
    verbose_print('Pushing variable onto stack: let ${0} := {1}'.format(name, value))
    variable_stack.append((name, value))


def value_of_variable(name):
    if len(variable_stack) > 0:
        for index in range(len(variable_stack) - 1, -1, -1):
            if variable_stack[index][NAME] == name:
                reverse_index = len(variable_stack) - (index + 1)
                verbose_print('Variable "{0}" found on stack (position {1}).'.format(name, reverse_index))
                return variable_stack[index][VALUE]

    verbose_print('Variable "{0}" NOT FOUND on variable stack.'.format(name))
    return None
