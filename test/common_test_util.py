from textwrap import dedent

from hq.soup_util import make_soup


def capture_stderr_output(capsys):
    _, output = capsys.readouterr()
    return eliminate_blank_lines(output.strip())


def capture_stdout_output(capsys, strip=True):
    output, _ = capsys.readouterr()
    output = output.rstrip('\n')
    return eliminate_blank_lines(output.strip()) if strip else output


def eliminate_blank_lines(s):
    return '\n'.join([line for line in s.split('\n') if line.strip() != ''])


def expected_result(contents):
    return dedent(contents.lstrip('\n'))


def simulate_args_dict(**kwargs):
    args = {'<expression>': '', '--preserve': False, '-u': False, '--ugly': False, '-v': False}
    for key, value in kwargs.items():
        if key == 'expression':
            format_string = '<{0}>'
        elif len(key) == 1:
            format_string = '-{0}'
        else:
            format_string = '--{0}'
        args[format_string.format(key)] = value
    return args


def soup_with_body(contents):
    return make_soup(wrap_html_body(contents))


def wrap_html_body(contents):
    return '<html><body>{0}</body></html>'.format(contents)
