from cbox import cliparser

EXECUTOR_ATTR = '_executor_type'

CMD = 'cmd'
STREAM = 'STREAM'

__all__ = ('get_func_executor', 'EXECUTOR_ATTR', 'CMD', 'STREAM', )


def get_func_executor(func):
    executor_type = getattr(func, EXECUTOR_ATTR, None)
    try:
        return _executors_mapping[executor_type]
    except KeyError:
        raise ValueError(
            'unknown executor_type %s for function %s. did you decorated '
            'your function?' % (executor_type, func.__name__)
        )


def _execute_stream(func, argv, input_stream, output_stream):
    parser = cliparser.get_cli_parser(func, skip_first=1)
    func_kwargs = cliparser.parse_args(parser, argv=argv)
    return func(input_stream, output_stream, **func_kwargs)


def _execute_cmd(func, argv, input_stream, output_stream):
    parser = cliparser.get_cli_parser(func, skip_first=0)
    func_kwargs = cliparser.parse_args(parser, argv=argv)
    return func(**func_kwargs)


_executors_mapping = {
    CMD: _execute_cmd,
    STREAM: _execute_stream,
}
