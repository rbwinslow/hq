from hq.xpath.object_type import is_number

exports = ['number']


class number:

    def __init__(self, obj):
        if isinstance(obj, number):
            self.value = obj.value
        else:
            try:
                self.value = float(obj)
            except ValueError:
                self.value = float('nan')

    def __str__(self):
        return str(self.value)

    def __add__(self, other):
        return number(self.value + other.value)

    def __eq__(self, other):
        return is_number(other) and self.value == other.value

    def __float__(self):
        return self.value
