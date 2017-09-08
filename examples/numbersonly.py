#!/usr/bin/env python3
import cbox


@cbox.stream()
def numbersonly(line):
    """returns the lines containing only numbers. bad lines reported to stderr.
    if any bad line is detected, exits with exitcode 2.
    """
    if not line.isnumeric():
        raise ValueError('{} is not a number'.format(line))
    return line


if __name__ == '__main__':
    cbox.main(numbersonly)
