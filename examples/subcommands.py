#!/usr/bin/env python3
import sys; sys.path.append('.')
import cbox


@cbox.cmd
def hello(name: str):
    """greets a person by its name.

    :param name: the name of the person
    """
    print('hello name={name}!'.format(**locals()))

@cbox.cmd
def world(name: str):
    """greets a person by its name.

    :param name: the name of the person
    """
    print('world name={name}!'.format(**locals()))


if __name__ == '__main__':
    cbox.main([hello, world])
