import re

from hq.hq import main
from test.common_test_util import simulate_args_dict, wrap_html_body, capture_stdout_output, capture_stderr_output


def test_preserve_flag_turns_off_space_normalization(capsys, mocker):
    expected = '   PyCharm     rocks!    '
    mocker.patch('hq.hq.docopt').return_value = simulate_args_dict(expression='`${//p}`', preserve=True)
    mocker.patch('sys.stdin.read').return_value = wrap_html_body('<p>{0}</p>'.format(expected))

    main()

    assert capture_stdout_output(capsys, strip=False) == expected


def test_ugly_flag_preserves_markup_formatting(capsys, mocker):
    expected = '<p>I, too, enjoy PyCharm.</p>'
    mocker.patch('hq.hq.docopt').return_value = simulate_args_dict(expression='//p', ugly=True)
    mocker.patch('sys.stdin.read').return_value = wrap_html_body(expected)

    main()

    assert capture_stdout_output(capsys) == expected


def test_syntax_error_prints_proper_error_message(capsys, mocker):
    mocker.patch('hq.hq.docopt').return_value = simulate_args_dict(expression='child:://')
    mocker.patch('sys.stdin.read').return_value = wrap_html_body('')

    main()

    assert re.match(r'^syntax error.+expected.+name.+got.+slash', capture_stderr_output(capsys).lower())


def test_query_error_prints_proper_error_message(capsys, mocker):
    mocker.patch('hq.hq.docopt').return_value = simulate_args_dict(expression='no-such-function()')
    mocker.patch('sys.stdin.read').return_value = wrap_html_body('')

    main()

    assert re.match(r'^query error.+unknown function.+no-such-function', capture_stderr_output(capsys).lower())
