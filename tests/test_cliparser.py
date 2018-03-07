import pytest

import cbox
from cbox import cliparser


@pytest.mark.parametrize('docstring,help_msg, params', [
    (
        'this is a function\n    that is doing something.\n    \n    :param int x: bla\n    :param str y: x\n    ',  # noqa
        'this is a function\nthat is doing something.',
        {'x': ('int', 'bla'), 'y': ('str', 'x')}
    ),
    (
        'this is a function\n    that is doing something.\n    \n    :param int x: first    \nsecond    \n    :param str y: x is better than y\n    ',  # noqa
        'this is a function\nthat is doing something.',
        {'x': ('int', 'first\nsecond'), 'y': ('str', 'x is better than y')}
    ),
    (
        '    only help message in docstring',
        'only help message in docstring',
        {}
    ),
    (None, None, {}),
    ('', None, {}),
    (
        '    :param int x: first arg    \n    :param str y: second arg',
        None,
        {'x': ('int', 'first arg'), 'y': ('str', 'second arg')},
    ),
    (
        '    :param x: first arg    \n    :param y: second arg',
        None,
        {'x': (None, 'first arg'), 'y': (None, 'second arg')},
    ),
])
def test__parse_docstring(docstring, help_msg, params):
    output_msg, output_params = cliparser._parse_docstring(docstring)
    assert output_msg == help_msg
    assert output_params == params


def test_cli_docstring_help():
    @cbox.stream()
    def nth_item(line, n: int = 0):
        """returns the nth item from each line.

        :param n: the number of item position starting from 0
        """
        return line.split()[n]

    parser = cliparser.get_cli_parser(nth_item, skip_first=1)
    output = parser.format_help()

    expected = 'usage: %s [-h] [-n N]\n\nreturns the nth item from each ' \
               'line.\n\noptional arguments:\n  -h, --help  ' \
               'show this help message and exit\n  -n N        ' \
               'the number of item position starting from 0\n' % parser.prog

    assert output == expected


def test_get_cli_parser_func_with_kwargs_raises():
    @cbox.stream()
    def func(**kargs):
        pass

    with pytest.raises(ValueError):
        cliparser.get_cli_parser(func)


def test_get_cli_multi_func():
    @cbox.cmd
    def func1(arg1):
        """ description of func1

        :param str arg1: desc1
        :return:
        """
        pass

    @cbox.cmd
    def func2(arg1, arg2):
        """ description of func2

        :param str arg1: desc1
        :param str arg2: desc2
        :return:
        """
        pass

    parser = cliparser.get_cli_multi_parser([func1, func2], skip_first=1)
    expected = """usage: %s [-h] {func1,func2} ...

which subcommand do you want?

optional arguments:
  -h, --help     show this help message and exit

subcommands:
  {func1,func2}
    func1        description of func1
    func2        description of func2
"""
    output = parser.format_help()
    print(output)
    assert output == expected % parser.prog

