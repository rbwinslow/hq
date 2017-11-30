import math

from hq.hquery.evaluation_error import HqueryEvaluationError
from hq.soup_util import is_any_node
from hq.hquery.object_type import is_number, is_node_set, string_value, is_boolean
from hq.hquery.sequences import make_sequence

exports = ('ceiling', 'floor', 'number', 'round_', 'sum')


class number:

    def __init__(self, obj):
        if isinstance(obj, number):
            self.value = obj.value
        elif is_boolean(obj):
            self.value = 1 if obj else 0
        elif is_node_set(obj) or is_any_node(obj):
            self.value = self._int_or_float(float(string_value(obj)))
        else:
            try:
                self.value = self._int_or_float(float(obj))
            except ValueError:
                self.value = float('nan')

    def __float__(self):
        return float(self.value)

    def __int__(self):
        return int(self.value)

    def __str__(self):
        result = str(self.value)
        if result == 'nan':
            result = 'NaN'
        return result

    def __hash__(self):
        return self.value.__hash__()

    def __add__(self, other):
        return number(self.value + self._value_of_other_operand(other))

    def __sub__(self, other):
        return number(self.value - self._value_of_other_operand(other))

    def __neg__(self):
        return number(-self.value)

    def __mul__(self, other):
        return number(self.value * self._value_of_other_operand(other))

    def __div__(self, other):
        return self.__truediv__(other)

    def __truediv__(self, other):
        other = self._value_of_other_operand(other)
        if other == 0:
            return number(float('nan'))
        else:
            return number(self.value / other)

    def __mod__(self, other):
        return number(self.value % self._value_of_other_operand(other))

    def __eq__(self, other):
        return self.value == self._value_of_other_operand(other)

    def __ge__(self, other):
        return self.value >= self._value_of_other_operand(other)

    def __gt__(self, other):
        return self.value > self._value_of_other_operand(other)

    def __le__(self, other):
        return self.value <= self._value_of_other_operand(other)

    def __lt__(self, other):
        return self.value < self._value_of_other_operand(other)

    def __repr__(self):
        return 'number({0})'.format(str(self.value))

    @staticmethod
    def _int_or_float(numeric_value):
        if isinstance(numeric_value, int) or numeric_value % 1 != 0:
            return numeric_value
        else:
            return int(numeric_value)

    @staticmethod
    def _value_of_other_operand(other):
        return other.value if is_number(other) else other


def ceiling(value):
    return number(math.ceil(value.value))


def floor(value):
    return number(math.floor(value.value))


def round_(*args):
    if len(args) == 0:
        raise HqueryEvaluationError('round() function requires at least one argument')
    value = args[0]
    if math.isnan(value.value):
        return value
    else:
        return number(round(value.value, 0 if len(args) < 2 else args[1].value))


def sum(*args):
    if len(args) >= 1:
        sequence = make_sequence(args[0])
    else:
        sequence = make_sequence([])
    if len(args) >= 2:
        zero = args[1]
    else:
        zero = number(0)

    if len(sequence) == 0:
        return zero
    else:
        result = number(0)
        for item in sequence:
            result += number(item)
        return result
