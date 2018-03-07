#!/usr/bin/env python3
import sys; sys.path.append('.')
import cbox



@cbox.cmd
def hello(name: str):
    """greets a person by its name.

    :param name: the name of the person
    """
    print(f'hello name={name}!')

@cbox.cmd
def world(name: str):
    """greets a person by its name.

    :param name: the name of the person
    """
    print(f'world name={name}!')


if __name__ == '__main__':
    cbox.main([hello, world])
