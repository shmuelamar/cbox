import asyncio
import os
from os import linesep
import re
import threading
from io import StringIO
from itertools import product
from string import ascii_letters

import pytest

import cbox

_here = os.path.dirname(os.path.abspath(__file__))
DATA1 = linesep.join(['hello world', 'my name is ddd', 'bye bye', 'hi', ''])
DATA2 = linesep.join(['hello', 'world', ''])
NUMBERS = linesep.join([str(i) for i in range(1000)])


def run_cli(func, in_data, argv=(), expected_exitcode=0, return_stderr=False):
    """runs `func` using `cbox.run()` and returns its output stream content"""
    outstream = StringIO()
    errstream = StringIO()
    instream = StringIO(in_data)

    exitcode = cbox.main(
        func, argv, instream, outstream, errstream, exit=False
    )

    assert expected_exitcode == exitcode

    outstream.seek(0)
    errstream.seek(0)

    if return_stderr:
        return outstream.read(), errstream.read()

    assert not errstream.read()
    return outstream.read()


def test_run_cli_helper():
    @cbox.stream()
    def identity(line, x: int, y=2):
        assert x == 1
        assert y == 2
        return line

    assert run_cli(identity, DATA1, argv=['-x', '1']) == DATA1


def test_run_cli_helper_stderr():
    @cbox.stream()
    def identity(line):
        raise ValueError('hello')

    out, err = run_cli(
        identity, DATA1, return_stderr=True, expected_exitcode=2
    )
    assert not out
    assert 'ValueError' in err


def test_cmd():
    msg = []

    @cbox.cmd
    def hello(name):
        msg.append(name)
        return 0

    run_cli(hello, None, argv=['--name', 'test'])
    assert msg == ['test']


def test_multi_cmd():
    msg = []

    @cbox.cmd
    def func1(arg1):
        """ description of func1

        :param str arg1: desc1
        :return:
        """
        msg.clear()
        msg.append('func1: arg1={}'.format(arg1))
        return 0

    @cbox.cmd
    def func2(arg1, arg2):
        """ description of func2

        :param str arg1: desc1
        :param str arg2: desc2
        :return:
        """
        msg.clear()
        msg.append("func2: arg1={} arg2={}".format(arg1, arg2))
        return 0

    run_cli([func1, func2], None, argv="func1 --arg1 1".split(' '))
    assert msg[0] == "func1: arg1=1"

    run_cli([func1, func2], None, argv="func2 --arg1 1 --arg2 2".split(' '))
    assert msg[0] == "func2: arg1=1 arg2=2"


def test_cli_simple_func():
    @cbox.stream()
    def first(line):
        return line.split(' ', 1)[0]

    assert run_cli(first, DATA1).splitlines() == ['hello', 'my', 'bye', 'hi']


def test_cli_worker_type_simple():
    @cbox.stream(worker_type='simple', max_workers=4)
    def simple(line):
        return str(threading.get_ident())

    lines = run_cli(simple, DATA1).splitlines()
    assert len(lines) == 4
    assert len(set(lines)) == 1


def test_cli_threads():
    @cbox.stream(worker_type='thread', max_workers=4)
    def threaded(line):
        return line + str(threading.get_ident())

    lines = run_cli(threaded, DATA1).splitlines()
    assert len(lines) == len(set(lines)) == 4


def test_cli_arg():
    @cbox.stream()
    def firstn(line, n: int):
        return ' '.join(line.split(' ', n)[:n])

    assert run_cli(firstn, DATA1, argv=['-n', '1']).splitlines() == \
        ['hello', 'my', 'bye', 'hi']

    assert run_cli(firstn, DATA1, argv=['-n', '2']).splitlines() == \
        ['hello world', 'my name', 'bye bye', 'hi']


def test_cli_default_arg():
    @cbox.stream()
    def firstn(line, n=1):
        return ' '.join(line.split(' ', n)[:n])

    assert run_cli(firstn, DATA1).splitlines() == ['hello', 'my', 'bye', 'hi']

    assert run_cli(firstn, DATA1, argv=['-n', '2']).splitlines() == \
        ['hello world', 'my name', 'bye bye', 'hi']


def test_cli_chars():
    @cbox.stream(input_type='chars')
    def next_char(char):
        pos = ascii_letters.find(char)
        if pos != -1:
            char = ascii_letters[(pos + 1) % len(ascii_letters)]
        return str(char)

    assert run_cli(next_char, DATA2) == \
        'ifmmp{}xpsme{}'.format(linesep, linesep)


def test_cli_raw():
    @cbox.stream(input_type='raw')
    def sum_numbers(data):
        total = sum(int(ch) for ch in data)
        return str(total)

    assert run_cli(sum_numbers, '1234') == '10'


def test_cbox_list_output():
    @cbox.stream()
    def get_domains(line):
        return re.findall(r'(?:\w+\.)+\w+', line)

    lines = run_cli(get_domains, 'google.com facebook.com\nab\n').splitlines()
    assert lines == ['google.com', 'facebook.com']


def test_cbox_filtering():
    @cbox.stream()
    def get_domains(line):
        return re.findall(r'(?:\w+\.)+\w+', line) or None

    lines = run_cli(get_domains, 'google.com facebook.com\nab\n').splitlines()
    assert lines == ['google.com', 'facebook.com']


@pytest.mark.parametrize('exc,worker_type', product(
    [StopIteration, cbox.Stop], ['thread', 'simple']
))
def test_cbox_stop_iteration(exc, worker_type):
    line_counter = 0

    @cbox.stream(worker_type=worker_type)
    def head(line, n: int):
        nonlocal line_counter

        line_counter += 1
        if line_counter > n:
            raise exc()

        return line

    lines = run_cli(head, 'one\ntwo\nthree\n', ['-n', '2']).splitlines()
    assert lines == ['one', 'two']


def test_cbox_threads_stop_iteration():
    line_counter = 0

    @cbox.stream(worker_type='thread', max_workers=4)
    def head(line, n: int):
        nonlocal line_counter

        line_counter += 1
        if line_counter > n:
            raise StopIteration()

        return line

    lines = run_cli(head, 'one\ntwo\nthree\n', ['-n', '2']).splitlines()
    assert lines == ['one', 'two']


def test_cbox_threads_ordered():
    @cbox.stream(worker_type='thread', workers_window=100)
    def identity(line):
        return line

    lines = run_cli(identity, NUMBERS).splitlines()
    assert len(lines) == 1000
    assert lines == NUMBERS.splitlines()


def test_cbox_exitcode_0_no_error():
    @cbox.stream()
    def identity(line):
        return line

    with pytest.raises(SystemExit) as err:
        cbox.main(identity, [], StringIO(DATA1), StringIO(), StringIO())
        assert err.status == 0


def test_cbox_exitcode_2_on_error():
    @cbox.stream()
    def raiser(line):
        raise Exception()

    with pytest.raises(SystemExit) as err:
        cbox.main(raiser, [], StringIO(DATA1), StringIO(), StringIO())
        assert err.status == 2


@pytest.mark.parametrize('worker_type', ['simple', 'thread'])
def test_cbox_stderr(worker_type):
    @cbox.stream(worker_type=worker_type)
    def digitsonly(line):
        if not line.isnumeric():
            raise ValueError('ignoring - not digit')
        return line

    out, errout = run_cli(
        digitsonly, '1\na\n2\n', return_stderr=True, expected_exitcode=2
    )
    assert out.splitlines() == ['1', '2']
    assert 'ignoring - not digit' in errout


def test_cbox_asyncio_stop_iteration():
    line_counter = 0

    @cbox.stream(worker_type='asyncio')
    async def head(line, n: int):
        nonlocal line_counter

        await asyncio.sleep(0.01)
        if line_counter >= n:
            raise cbox.Stop()

        line_counter += 1
        return line

    lines = run_cli(head, 'one\ntwo\nthree\n', ['-n', '2']).splitlines()
    assert lines == ['one', 'two']


def test_cbox_asyncio_ordered():
    @cbox.stream(worker_type='asyncio', workers_window=100)
    async def asleep(line):
        await asyncio.sleep(0.01)
        return line

    lines = run_cli(asleep, NUMBERS).splitlines()
    assert len(lines) == 1000
    assert lines == NUMBERS.splitlines()


def test_cbox_asyncio_uses_event_loop():
    async def sleepy(x):
        await asyncio.sleep(0.01)
        return x

    @cbox.stream(worker_type='asyncio', workers_window=100)
    async def asleep(line):
        loop = asyncio.get_event_loop()
        fut = asyncio.ensure_future(sleepy(line), loop=loop)
        await fut
        return fut.result()

    lines = run_cli(asleep, NUMBERS).splitlines()
    assert len(lines) == 1000
    assert lines == NUMBERS.splitlines()
