#!/usr/bin/env python3
import asyncio

import cbox


@cbox.stream(worker_type='asyncio', workers_window=30)
async def tcping(domain, timeout: int=3):
    loop = asyncio.get_event_loop()

    fut = asyncio.open_connection(domain, 80, loop=loop)
    try:
        reader, writer = await asyncio.wait_for(fut, timeout=timeout)
        writer.close()
        status = 'up'
    except (OSError, asyncio.TimeoutError):
        status = 'down'

    return '{} is {}'.format(domain, status)


if __name__ == '__main__':
    cbox.main(tcping)
