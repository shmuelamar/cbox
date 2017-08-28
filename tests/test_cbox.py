import os
import threading
from io import StringIO
from string import ascii_letters

import pytest

import cbox

_here = os.path.dirname(os.path.abspath(__file__))
DATA1 = 'hello world\nmy name is ddd\nbye bye\nhi\n'
DATA2 = 'hello\nworld\n'


def run_cli(func, in_data, argv=()):
    """runs `func` using `cbox.run()` and returns its output stream content"""
    outstream = StringIO()
    instream = StringIO(in_data)

    cbox.run(func, argv, instream, outstream)

    outstream.seek(0)
    return outstream.read()


def test_run_cli_helper():
    @cbox.cli()
    def identity(line, x: int, y=2):
        assert x == 1
        assert y == 2
        return line

    assert run_cli(identity, DATA1, argv=['-x', '1']) == DATA1


def test_cli_simple_func():
    @cbox.cli()
    def first(line):
        return line.split(' ', 1)[0]

    assert run_cli(first, DATA1) == 'hello\nmy\nbye\nhi\n'


def test_cli_worker_type_simple():
    @cbox.cli(worker_type='simple', max_workers=4)
    def simple(line):
        return str(threading.get_ident())

    lines = run_cli(simple, DATA1).splitlines()
    assert len(lines) == 4
    assert len(set(lines)) == 1


def test_cli_threads():
    @cbox.cli(worker_type='thread', max_workers=4)
    def threaded(line):
        return line + str(threading.get_ident())

    lines = run_cli(threaded, DATA1).splitlines()
    assert len(lines) == len(set(lines)) == 4


@pytest.mark.skip('subprocess not supported yet')
def test_cli_subprocess():
    @cbox.cli(worker_type='subprocess', max_workers=4)
    def subprocessed(line):
        return line + str(threading.get_ident())

    lines = run_cli(subprocessed, DATA1).splitlines()
    assert len(lines) == len(set(lines)) == 4


def test_cli_arg():
    @cbox.cli()
    def firstn(line, n: int):
        return ' '.join(line.split(' ', n)[:n])

    assert run_cli(firstn, DATA1, argv=['-n', '1']) == \
        'hello\nmy\nbye\nhi\n'

    assert run_cli(firstn, DATA1, argv=['-n', '2']) == \
        'hello world\nmy name\nbye bye\nhi\n'


def test_cli_default_arg():
    @cbox.cli()
    def firstn(line, n=1):
        return ' '.join(line.split(' ', n)[:n])

    assert run_cli(firstn, DATA1) == 'hello\nmy\nbye\nhi\n'

    assert run_cli(firstn, DATA1, argv=['-n', '2']) == \
        'hello world\nmy name\nbye bye\nhi\n'


def test_cli_chars():
    @cbox.cli(input_type='chars')
    def next_char(char):
        pos = ascii_letters.find(char)
        if pos != -1:
            char = ascii_letters[(pos + 1) % len(ascii_letters)]
        return str(char)

    assert run_cli(next_char, DATA2) == 'ifmmp\nxpsme\n'


def test_cli_raw():
    @cbox.cli(input_type='raw')
    def sum_numbers(data):
        total = sum(int(ch) for ch in data)
        return str(total)

    assert run_cli(sum_numbers, '1234') == '10'
