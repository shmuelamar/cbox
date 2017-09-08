import sys
from functools import wraps
from sys import stdin, stdout, stderr

from cbox import executors
from . import concurrency, streams

__all__ = ('stream', 'cmd', 'main', )


def stream(input_type='lines', output_type=None, worker_type='simple',
           max_workers=1, workers_window=100):
    """wrapper for processing data from input stream into output into output
    stream while passing each data piece into the function.
    function should take at least one argument (an input stream piece) and
    return an `str` to be written into the output stream.

    Example Usage:

        >>> import cbox
        >>>
        >>> @cbox.stream()
        >>> def firstchar(line):
        >>>    '''extracts the first char out of each line'''
        >>>    return line[0] if line else ''


    :param str input_type: defines how the input stream is split. one of
      `lines`, `chars` or `raw`.
    :param str output_type: defines how to write into output stream
      (similarly to input stream). if `None`, split the output stream in the
      same way of `input_type`. one of `None`, `lines`, `chars` or `raw`.
    :param str worker_type: one of `simple` or `thread`.
    :param int max_workers: how many max workers (e.g. threads) to run in
      parallel. only affect if `worker_type=thread`.
    :param int workers_window: how many tasks to execute in parallel before
      waiting for them to be completed. only affect if `worker_type=thread`.
    """
    def inner(f):

        @wraps(f)
        def wrapper(input_stream, output_stream, error_stream, **kwargs):
            in_parser = streams.get_input_parser(input_type)
            out_parser = streams.get_output_parser(output_type, input_type)
            runner = concurrency.get_runner(
                worker_type=worker_type,
                max_workers=max_workers,
                workers_window=workers_window,
            )
            items = in_parser(input_stream)
            output = runner(f, items, kwargs)
            return out_parser(output_stream, error_stream, output)

        setattr(wrapper, executors.EXECUTOR_ATTR, executors.STREAM)
        return wrapper
    return inner


def cmd(f):
    """wrapper for easily exposing a function as a CLI command.
    including help message, arguments help and type.

    Example Usage:

        >>> import cbox
        >>>
        >>> @cbox.cmd
        >>> def hello(name: str):
        >>>     '''greets a person by its name.
        >>>
        >>>     :param name: the name of the person
        >>>     '''
        >>>     print('hello {}!'.format(name))

    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    setattr(wrapper, executors.EXECUTOR_ATTR, executors.CMD)
    return wrapper


def main(func=None, argv=None, input_stream=stdin, output_stream=stdout,
         error_stream=stderr, exit=True):
    """runs a function as a command.
    runs a function as a command - reading input from `input_stream`, writing
    output into `output_stream` and providing arguments from `argv`.

    Example Usage:

        >>> import cbox
        >>>
        >>> @cbox.cmd
        >>> def hello(name: str):
        >>>     print('hello {}!'.format(name))
        >>>
        >>> if __name__ == '__main__':
        >>>    cbox.main(hello)

    more examples on `README.md`


    :param callable func: the function to execute, must be decorated by
      `@cbox.cmd` or `@cbox.stream`.
    :param list[str] argv: command arguments (default `sys.argv`)
    :param input_stream: readable file-like object (default `stdin`)
    :param output_stream: writable file-like object (default `stdout`)
    :param error_stream: writable file-like object (default `stderr`)
    :param bool exit: if True, exits (i.e. `sys.exit(exitcode)`)
      with the `exitcode`, else returns the `exitcode`.
      the code is 0 if no errors, else 2.
    :return: the exit code if `exit` is False, else raises `SystemExit(code)`
    """
    executor = executors.get_func_executor(func)
    exitcode = executor(func, argv, input_stream, output_stream, error_stream)

    if exit:
        sys.exit(exitcode)
    return exitcode
