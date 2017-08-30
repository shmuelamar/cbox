from concurrent.futures import ThreadPoolExecutor
from functools import partial
from itertools import islice

__all__ = ('get_runner', 'SIMPLE', 'THREAD', )

SIMPLE = 'simple'
THREAD = 'thread'


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
        futures = [pool.submit(func, item, **kwargs)
                   for item in islice(items, workers_window)]
        yield from [f.result() for f in futures]


def _simple_runner(func, items, kwargs, *, max_workers, workers_window):
    for item in items:
        yield func(item, **kwargs)


# TODO: add asyncio
# TODO: add subprocess
_runners_mapping = {
    SIMPLE: _simple_runner,
    THREAD: _thread_runner,
}
