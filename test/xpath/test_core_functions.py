import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

from ..test_util import expected_result, process_xpath_query


def test_number_function_converts_string_to_number():
    actual = process_xpath_query('', 'number("43") + number("-1")')
    assert actual == expected_result('42.0')
