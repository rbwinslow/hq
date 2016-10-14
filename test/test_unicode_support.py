from hq.hq import main
from test.common_test_util import expected_result, wrap_html_body, simulate_args_dict, capture_console_output


def test_tolerates_latin_characters_in_element_contents(capsys, mocker):
    mocker.patch('hq.hq.docopt').return_value = simulate_args_dict(expression='//div')
    mocker.patch('sys.stdin.read').return_value = wrap_html_body(u"""
    <div>
        T\xeate\xa0\xe0\xa0t\xeate
    </div>""")

    main()

    actual, _ = capture_console_output(capsys)
    assert actual == expected_result(u"""
    <div>
     T\xeate\xa0\xe0\xa0t\xeate
    </div>""")


def test_tolerates_latin_characters_in_attribute_contents(capsys, mocker):
    mocker.patch('hq.hq.docopt').return_value = simulate_args_dict(expression='//div/@role')
    mocker.patch('sys.stdin.read').return_value = wrap_html_body(u"""
    <div role="prim\xe4r">
    </div>""")

    main()

    actual, _ = capture_console_output(capsys)
    assert actual == expected_result(u'role="prim\xe4r"')


def test_tolerates_latin_characters_in_comments(capsys, mocker):
    mocker.patch('hq.hq.docopt').return_value = simulate_args_dict(expression='//comment()')
    mocker.patch('sys.stdin.read').return_value = wrap_html_body(u"""
    <!-- sacr\xe9 bleu! -->""")

    main()

    actual, _ = capture_console_output(capsys)
    assert actual == expected_result(u'<!-- sacr\xe9 bleu! -->')
