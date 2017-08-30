#!/usr/bin/env python3
import codecs
import cbox


@cbox.stream(input_type='chars')
def rot13(char):
    """replace each english letter 13 letters next"""
    return codecs.encode(char, 'rot_13')


if __name__ == '__main__':
    cbox.main(rot13)
