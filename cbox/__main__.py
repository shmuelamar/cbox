import argparse
import ast
import sys
from sys import stdin, stdout, stderr

import cbox
from cbox import concurrency

__all__ = ('get_inline_func', 'main', )


def _inline2func(inline_str, inline_globals, **stream_kwargs):
    if stream_kwargs.get('worker_type') != concurrency.ASYNCIO:
        @cbox.stream(**stream_kwargs)
        def inline(s):
            return eval(inline_str, inline_globals, locals())
    else:
        @cbox.stream(**stream_kwargs)
        async def inline(s):
            return eval(inline_str, inline_globals, locals())

    return inline


def _import_inline_modules(modules=None):
    inline_globals = globals()
    if not modules:
        return inline_globals

    for m in modules.split(','):
        inline_globals[m] = __import__(m, inline_globals)
    return inline_globals


def _is_compilable(s):
    """returns True if the string is compilable, False otherwise"""
    try:
        ast.parse(s)
        return True
    except Exception:
        return False


def _parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description='runs the inline statement using eval() for each input on '
                    'stdin and outputs the results to stdout',
    )
    parser.add_argument('inline')
    parser.add_argument(
        '-m', '--modules', default=None,
        help='comma separated list of modules to import',
    )
    parser.add_argument(
        '-t', '--input-type', default='lines',
        help='defines how the input stream is split',
        choices=('lines', 'chars', 'raw')
    )
    parser.add_argument(
        '-w', '--worker-type', default='simple',
        choices=('simple', 'thread', 'asyncio'),
        help='worker type to use for concurrency',
    )
    parser.add_argument(
        '-c', '--max-workers', default=1, type=int,
        help='how many max workers (i.e. threads) to run in parallel. '
             'only affect if --worker-type is thread',
    )
    parser.add_argument(
        '--workers-window', default=100, type=int,
        help='how many tasks to execute in parallel before waiting for them '
             'to be completed. only affect if --worker-type is not simple.',
    )
    return parser.parse_args(argv)


def get_inline_func(inline_str, modules=None, **stream_kwargs):
    """returns a function decorated by `cbox.stream` decorator.

    :param str inline_str: the inline function to execute,
      can use `s` - local variable as the input line/char/raw
      (according to `input_type` param).
    :param str modules: comma separated list of modules to import before
      running the inline function.
    :param dict stream_kwargs: optional arguments to `cbox.stream` decorator
    :rtype: callable
    """
    if not _is_compilable(inline_str):
        raise ValueError(
            'cannot compile the inline expression - "%s"' % inline_str
        )

    inline_globals = _import_inline_modules(modules)
    func = _inline2func(inline_str, inline_globals, **stream_kwargs)
    return func


def main(argv=None, input_stream=stdin, output_stream=stdout,
         error_stream=stderr):
    """runs inline function - more info run `cbox --help`"""
    args = _parse_args(argv)
    args_dict = args.__dict__.copy()
    inline_str = args_dict.pop('inline')
    modules = args_dict.pop('modules')

    func = get_inline_func(inline_str, modules, **args_dict)

    return cbox.main(
        func=func, argv=[], input_stream=input_stream,
        output_stream=output_stream, error_stream=error_stream, exit=False,
    )


if __name__ == '__main__':  # pragma: nocover
    sys.exit(main())
