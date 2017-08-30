#!/usr/bin/env python3
import cbox


@cbox.stream()
# we can pass default values and use type annotations for correct types
def nth_item(line, n: int = 0):
    """returns the nth item from each line.

    :param n: the number of item position starting from 0
    """
    return line.split()[n]


if __name__ == '__main__':
    cbox.main(nth_item)
