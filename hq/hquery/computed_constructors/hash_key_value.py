from hq.hquery.object_type import debug_dump_anything
from hq.verbosity import verbose_print


class ComputedHashKeyValueConstructor:

    def __init__(self, key):
        self.key = key
        self.value_fn = None


    def set_value(self, fn):
        self.value_fn = fn


    def evaluate(self):
        verbose_print('Evaluating value expression for constructed hash key "{0}"'.format(self.key), indent_after=True)

        value = self.value_fn()

        msg = u'Finished evaluating; value of constructed hash key "{0}" is {1}'
        verbose_print(lambda: msg.format(self.key, debug_dump_anything(value)), outdent_before=True)

        return HashKeyValue(self.key, value)



class HashKeyValue:

    def __init__(self, key, value):
        self.key = key
        self.value = value
