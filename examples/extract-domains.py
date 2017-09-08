#!/usr/bin/env python3
import re

import cbox


@cbox.stream()
def extract_domains(line):
    """tries to extract all the domains from the input using simple regex"""
    return re.findall(r'(?:\w+\.)+\w+', line) or None  # or None can be omitted


if __name__ == '__main__':
    cbox.main(extract_domains)
