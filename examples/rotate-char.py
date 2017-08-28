#!/usr/bin/env python3
import cbox
from string import ascii_letters


@cbox.cli(input_type='chars')
def rotate(char):
    """replace every english letter with the next letter"""
    pos = ascii_letters.find(char)
    if pos != -1:
        char = ascii_letters[(pos + 1) % len(ascii_letters)]
    return str(char)


if __name__ == '__main__':
    cbox.main(rotate)
