import os
from pathlib import Path

from bs4 import BeautifulSoup

from ..verbosity import set_verbosity


def pytest_addoption(parser):
    parser.addoption("--gabby",
                     action="store_true",
                     help="Print verbose (debug) information to stderr")


def pytest_configure(config):
    set_verbosity(bool(config.getvalue('--gabby')))


def pytest_generate_tests(metafunc):

    if 'name' in metafunc.fixturenames and \
                    'testfile' in metafunc.fixturenames and \
                    'testline' in metafunc.fixturenames and \
                    'language' in metafunc.fixturenames and \
                    'source' in metafunc.fixturenames and \
                    'expression' in metafunc.fixturenames and \
                    'expected_result' in metafunc.fixturenames:
        tests = []
        soup_names = set()
        test_dir = Path(os.path.realpath(__file__)).parent
        csstest_paths = list(test_dir.glob('*.csstests'))
        xpathtest_paths = list(test_dir.glob('*.xpathtests'))
        for test_path in csstest_paths:
            soup_names.add(test_path.stem)
        for test_path in xpathtest_paths:
            soup_names.add(test_path.stem)

        soups = _cook_soups(soup_names, test_path)

        _collect_tests('CSS', csstest_paths, soups, tests)
        _collect_tests('XPATH', xpathtest_paths, soups, tests)

        metafunc.parametrize('name,testfile,testline,language,source,expression,expected_result', tests)


def _cook_soups(soup_names, test_path):
    soups = {}
    for stem in soup_names:
        htmlname = '{0}/{1}.html'.format(test_path.parent, stem)
        with open(htmlname, 'r') as source:
            soups[stem] = BeautifulSoup(source.read().replace('\n', ''), 'html.parser')
    return soups


def _collect_tests(language, test_paths, soups, tests):
    current_name, current_expr, current_result = ('', '', '')
    READING_NAME, READING_EXPRESSION, READING_RESULT = range(3)
    currently = READING_NAME
    for test_path in test_paths:
        lineno, last_name_line = (0, 0)
        with open(str(test_path), 'r') as file:
            for line in file:
                lineno += 1
                line = line.rstrip()
                if currently == READING_NAME:
                    current_name = line
                    last_name_line = lineno
                    currently = READING_EXPRESSION
                elif currently == READING_EXPRESSION:
                    current_expr = line
                    currently = READING_RESULT
                elif currently == READING_RESULT:
                    if len(line) >= 4 and line[:4] == '----':
                        tests.append((current_name,
                                      test_path.parts[-1],
                                      last_name_line,
                                      language,
                                      soups[test_path.stem],
                                      current_expr,
                                      current_result))
                        current_result = ''
                        currently = READING_NAME
                    elif len(current_result) == 0:
                        current_result = line
                    else:
                        current_result += '\n{0}'.format(line)
        if len(current_result) > 0:
            tests.append((current_name,
                          test_path.parts[-1],
                          last_name_line,
                          language,
                          soups[test_path.stem],
                          current_expr,
                          current_result))
