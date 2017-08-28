from functools import wraps
from sys import stdin, stdout

from . import cliparser, runners, streams

__all__ = ('cli', 'main', 'run', )


# TODO: support @cli & @cli() + change on examples
def cli(input_type='lines', output_type=None, worker_type=None, max_workers=1,
        workers_window=100):
    """TBD"""
    def inner(f):

        @wraps(f)
        def wrapper(input_stream, output_stream, **kwargs):
            in_parser = streams.get_input_parser(input_type)
            out_parser = streams.get_output_parser(output_type, input_type)
            runner = runners.get_runner(
                worker_type=worker_type,
                max_workers=max_workers,
                workers_window=workers_window,
            )
            items = in_parser(input_stream)
            output = runner(f, items, kwargs)
            return out_parser(output_stream, output)

        return wrapper
    return inner


def run(func=None, argv=None, input_stream=stdin, output_stream=stdout):
    """TBD"""
    func = cliparser.resolve_func(func=func)
    parser = cliparser.get_cli_parser(func)
    func_kwargs = cliparser.parse_args(parser, argv=argv)
    func(input_stream, output_stream, **func_kwargs)


def main(func=None):
    """TBD"""
    return run(func)
