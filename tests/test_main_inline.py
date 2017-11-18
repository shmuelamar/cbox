from io import StringIO
from os import linesep

import pytest

from cbox.__main__ import main

DATA1 = linesep.join(['hello world', '123 456', 'zzz xxx'])
DATA2 = linesep.join(['abc.py', 'def.pyc'])


def run_inline(in_data, argv):
    """runs inline func and returns its stdout, stderr and exitcode"""
    outstream = StringIO()
    errstream = StringIO()
    instream = StringIO(in_data)

    exitcode = main(argv, instream, outstream, errstream)

    outstream.seek(0)
    errstream.seek(0)

    return outstream.read(), errstream.read(), exitcode


def test_main_inline():
    argv = ['s.split()[0]']
    out, err, code = run_inline(DATA1, argv)

    assert code == 0
    assert not err
    assert out.splitlines() == ['hello', '123', 'zzz']


def test_main_inline_modules():
    argv = ['-m', 'os,re', 're.findall(r"\.py[cx]?", os.path.splitext(s)[-1])']
    out, err, code = run_inline(DATA2, argv)

    assert code == 0
    assert not err
    assert out.splitlines() == ['.py', '.pyc']

    assert 're' not in globals(), 'inline imports affect global scope'
    assert 'os' not in globals(), 'inline imports affect global scope'


def test_main_inline_error():
    argv = ['s.split(']

    with pytest.raises(ValueError):
        run_inline(DATA1, argv)


def test_main_inline_asyncio():
    argv = ['-w', 'asyncio', 's.split()[0]']
    out, err, code = run_inline(DATA1, argv)

    assert code == 0
    assert not err
    assert out.splitlines() == ['hello', '123', 'zzz']
