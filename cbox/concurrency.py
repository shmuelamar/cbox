import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from itertools import islice

__all__ = ('get_runner', 'SIMPLE', 'THREAD', 'ASYNCIO', )

ASYNCIO = 'asyncio'
SIMPLE = 'simple'
THREAD = 'thread'


class Stop(Exception):
    """signals to stop the processing of in stream"""
    pass


STOP_EXCEPTIONS = (StopIteration, Stop)


def get_runner(worker_type, max_workers=None, workers_window=None):
    """returns a runner callable.

    :param str worker_type: one of `simple` or `thread`.
    :param int max_workers: max workers the runner can spawn in parallel.
    :param in workers_window: max number of jobs waiting to be done by the
      workers at any given time.
    :return:
    """
    worker_func = _runners_mapping[worker_type]
    return partial(
        worker_func, max_workers=max_workers, workers_window=workers_window
    )


def _thread_runner(func, items, kwargs, *, max_workers, workers_window):
    items = iter(items)

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        while True:
            futures = [pool.submit(func, item, **kwargs)
                       for item in islice(items, workers_window)]
            if not futures:
                break

            try:
                yield from _future_iter(futures)
            except STOP_EXCEPTIONS:
                break


def _simple_runner(func, items, kwargs, *, max_workers, workers_window):
    for item in items:
        try:
            yield func(item, **kwargs), None
        except STOP_EXCEPTIONS:
            break
        except Exception as e:
            yield None, e


def _asyncio_runner(func, items, kwargs, *, max_workers, workers_window):
    loop = asyncio.new_event_loop()

    try:
        while True:
            window = list(islice(items, workers_window))
            if not window:
                break

            tasks = [func(item, **kwargs) for item in window]
            futures = [asyncio.ensure_future(t, loop=loop) for t in tasks]
            gathered = asyncio.gather(
                *futures, loop=loop, return_exceptions=True
            )
            loop.run_until_complete(gathered)

            try:
                yield from _future_iter(futures)
            except STOP_EXCEPTIONS:
                break
    finally:
        loop.close()


def _future_iter(futures):
    for fut in futures:
        try:
            yield fut.result(), None
        except STOP_EXCEPTIONS:
            raise
        except Exception as e:
            yield None, e


# TODO: add subprocess
_runners_mapping = {
    SIMPLE: _simple_runner,
    THREAD: _thread_runner,
    ASYNCIO: _asyncio_runner,
}
