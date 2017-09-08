#!/usr/bin/env python3
import cbox

counter = 0


@cbox.stream()
def head(line, n: int):
    """returns the first `n` lines"""
    global counter
    counter += 1

    if counter > n:
        raise cbox.Stop()  # can also raise StopIteration()
    return line


if __name__ == '__main__':
    cbox.main(head)
