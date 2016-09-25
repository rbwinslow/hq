from hq.soup_util import is_any_node
from hq.hquery.object_type import is_number, is_node_set, string_value, is_boolean

exports = ['number']


class number:

    def __init__(self, obj):
        if isinstance(obj, number):
            self.value = obj.value
        elif is_boolean(obj):
            self.value = float(1 if obj else 0)
        elif is_node_set(obj) or is_any_node(obj):
            self.value = float(string_value(obj))
        else:
            try:
                self.value = float(obj)
            except ValueError:
                self.value = float('nan')

    def __float__(self):
        return self.value

    def __int__(self):
        return int(self.value)

    def __str__(self):
        return str(self.value)

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

    @staticmethod
    def _value_of_other_operand(other):
        return other.value if is_number(other) else other
