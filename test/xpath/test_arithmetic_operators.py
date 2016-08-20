import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

from ..test_util import expected_result, process_xpath_query


def test_addition_operator():
    actual = process_xpath_query('', '40+2')
    assert actual == expected_result('42.0')
