import re

try:
    from mock import mock_open
except ImportError:
    from unittest.mock import mock_open

from hq.hq import main
from test.common_test_util import simulate_args_dict, wrap_html_body, capture_console_output


def test_preserve_space_flag_turns_off_space_normalization(capsys, mocker):
    hquery = '`${//p}`'
    content_with_spaces = '   PyCharm     rocks!    '
    mocker.patch('sys.stdin.read').return_value = wrap_html_body('<p>{0}</p>'.format(content_with_spaces))

    mocker.patch('hq.hq.docopt').return_value = simulate_args_dict(expression=hquery, preserve='s')
    main()
    actual, _ = capture_console_output(capsys, strip=False)
    assert actual == content_with_spaces

    mocker.patch('hq.hq.docopt').return_value = simulate_args_dict(expression=hquery, preserve='')
    main()
    actual, _ = capture_console_output(capsys, strip=False)
    assert actual == 'PyCharm rocks!'


def test_preserve_space_flag_causes_non_breaking_spaces_to_be_how_shall_we_say_preserved(capsys, mocker):
    mocker.patch('sys.stdin.read').return_value = wrap_html_body(u'<p>non\u00a0breaking&nbsp;spaces?</p>')

    mocker.patch('hq.hq.docopt').return_value = simulate_args_dict(expression='//p/text()', preserve='s')
    main()
    actual, _ = capture_console_output(capsys)
    assert actual == u'non\u00a0breaking\u00a0spaces?'

    mocker.patch('hq.hq.docopt').return_value = simulate_args_dict(expression='//p/text()', preserve='')
    main()
    actual, _ = capture_console_output(capsys)
    assert actual == u'non breaking spaces?'


def test_ugly_flag_preserves_markup_formatting(capsys, mocker):
    expected = '<p>I, too, enjoy PyCharm.</p>'
    mocker.patch('hq.hq.docopt').return_value = simulate_args_dict(expression='//p', ugly=True)
    mocker.patch('sys.stdin.read').return_value = wrap_html_body(expected)

    main()

    actual, _ = capture_console_output(capsys, strip=False)
    assert actual == expected


def test_syntax_error_prints_proper_error_message(capsys, mocker):
    mocker.patch('hq.hq.docopt').return_value = simulate_args_dict(expression='child:://')
    mocker.patch('sys.stdin.read').return_value = wrap_html_body('')

    main()

    _, actual = capture_console_output(capsys)
    assert re.match(r'^syntax error.+expected.+name.+got.+slash', actual.lower())


def test_query_error_prints_proper_error_message(capsys, mocker):
    mocker.patch('hq.hq.docopt').return_value = simulate_args_dict(expression='no-such-function()')
    mocker.patch('sys.stdin.read').return_value = wrap_html_body('')

    main()

    _, actual = capture_console_output(capsys)
    assert re.match(r'^query error.+unknown function.+no-such-function', actual.lower())


def test_reading_input_from_a_file_instead_of_stdin(capsys, mocker):
    expected_filename = 'filename.html'
    mocked_open = mock_open(read_data=wrap_html_body('<p>foo</p>'))
    mocker.patch('hq.hq.docopt').return_value = simulate_args_dict(
        expression='//p/text()', file=expected_filename)
    mocker.patch('hq.hq.open', mocked_open, create=True)

    main()

    actual, _ = capture_console_output(capsys)
    mocked_open.assert_called_with(expected_filename)
    assert actual == 'foo'


def test_program_flag_reads_hquery_program_from_file(capsys, mocker):
    expected_filename = 'filename.hq'
    mocked_open = mock_open(read_data='''
                                        //p
                                        ->
                                        $_/text()''')
    mocker.patch('hq.hq.docopt').return_value = simulate_args_dict(
        program=expected_filename)
    mocker.patch('sys.stdin.read').return_value = wrap_html_body('<p>foo</p>')
    mocker.patch('hq.hq.open', mocked_open, create=True)

    main()

    actual, _ = capture_console_output(capsys)
    mocked_open.assert_called_with(expected_filename)
    assert actual == 'foo'
