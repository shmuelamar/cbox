#!/usr/bin/env python3
import cbox
from cbox import Arg

from sys import stdin


@cbox.cmd
def echo(n: Arg(int, True)=5):
    """repeat input n times.

    :param n: repeats number

    """

    lines = stdin.read()
    print(lines * n)


if __name__ == '__main__':
    cbox.main(echo)
