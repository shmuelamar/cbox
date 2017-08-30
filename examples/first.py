#!/usr/bin/env python3
import cbox


@cbox.stream()
def first(line):
    return line.split()[0]


if __name__ == '__main__':
    cbox.main(first)
