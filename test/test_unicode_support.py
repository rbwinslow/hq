from hq.hq import main
from test.common_test_util import expected_result, eliminate_blank_lines, wrap_html_body


def test_tolerates_latin_characters_in_element_contents(capsys, mocker):
    mocker.patch('hq.hq.docopt').return_value = _mock_arguments(expression='//div')
    mocker.patch('sys.stdin.read').return_value = wrap_html_body("""
    <div>
        T\xeate\xa0\xe0\xa0t\xeate
    </div>""")

    main()

    assert _capture_output(capsys) == expected_result(u"""
    <div>
     T\xeate\xa0\xe0\xa0t\xeate
    </div>""")


def test_tolerates_latin_characters_in_attribute_contents(capsys, mocker):
    mocker.patch('hq.hq.docopt').return_value = _mock_arguments(expression='//div/@role')
    mocker.patch('sys.stdin.read').return_value = wrap_html_body("""
    <div role="prim\xe4r">
    </div>""")

    main()

    assert _capture_output(capsys) == expected_result(u'role="prim\xe4r"')


def _capture_output(capsys):
    output, _ = capsys.readouterr()
    return eliminate_blank_lines(output.strip())


def _mock_arguments(**kwargs):
    args = {'<expression>': '', '-n': False, '-v': False, '-x': True}
    for key, value in kwargs.items():
        format_string = '<{0}>' if key == 'expression' else '-{0}'
        args[format_string.format(key)] = value
    return args
