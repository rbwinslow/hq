exports = ['number']


class number:

    def __init__(self, obj):
        if isinstance(obj, number):
            self.value = obj.value
        else:
            self.value = float(obj)

    def __str__(self):
        return str(self.value)

    def __add__(self, other):
        return number(self.value + other.value)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.value == other.value

    def __float__(self):
        return self.value
