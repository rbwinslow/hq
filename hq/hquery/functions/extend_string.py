from hq.hquery.object_type import string_value

exports = ['join']


def join(sequence, delimiter):
    return delimiter.join([string_value(x) for x in sequence])
