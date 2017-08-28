from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import partial
from itertools import islice

__all__ = ('get_runner', 'SIMPLE', 'THREAD', 'SUBPROCESS',)

SIMPLE = 'simple'
THREAD = 'thread'
SUBPROCESS = 'subprocess'


def get_runner(worker_type, max_workers=None, workers_window=None):
    """TBD"""
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


def _subprocess_runner(func, items, kwargs, *, max_workers, workers_window):
    items = iter(items)

    with ProcessPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(func, item, **kwargs)
                   for item in islice(items, workers_window)]
        yield from [f.result() for f in futures]


def _simple_runner(func, items, kwargs, *, max_workers, workers_window):
    for item in items:
        yield func(item, **kwargs)


# TODO: add asyncio
_runners_mapping = {
    None: _simple_runner,
    SIMPLE: _simple_runner,
    THREAD: _thread_runner,
    SUBPROCESS: _subprocess_runner,
}
