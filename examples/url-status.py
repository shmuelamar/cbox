#!/usr/bin/env python3
import cbox
import requests


@cbox.stream(worker_type='thread', max_workers=4)
def url_status(line):
    resp = requests.get(line)
    return f'{line} - {resp.status_code}'


if __name__ == '__main__':
    cbox.main(url_status)
