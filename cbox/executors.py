from cbox import cliparser

EXECUTOR_ATTR = '_executor_type'

CMD = 'cmd'
MULTI_CMD = 'multi-cmd'
STREAM = 'STREAM'

__all__ = ('get_func_executor', 'EXECUTOR_ATTR', 'CMD', 'MULTI_CMD', 'STREAM', )


def get_func_executor(func):
    if isinstance(func, (list, tuple)):
        executor_type = MULTI_CMD
    else:
        executor_type = getattr(func, EXECUTOR_ATTR, None)
    try:
        return _executors_mapping[executor_type]
    except KeyError:
        raise ValueError(
            'unknown executor_type %s for function %s. did you decorated '
            'your function?' % (executor_type, func.__name__)
        )


def _execute_stream(func, argv, input_stream, output_stream, error_stream):
    parser = cliparser.get_cli_parser(func, skip_first=1)
    func_kwargs = cliparser.parse_args(parser, argv=argv)
    return func(input_stream, output_stream, error_stream, **func_kwargs)


def _execute_cmd(func, argv, input_stream, output_stream, error_stream):
    parser = cliparser.get_cli_parser(func, skip_first=0)
    func_kwargs = cliparser.parse_args(parser, argv=argv)
    return func(**func_kwargs)


def _execute_multi_cmd(funcs, argv, input_stream, output_stream, error_stream):
    parser = cliparser.get_cli_multi_parser(funcs, skip_first=0)
    func_kwargs = cliparser.parse_args(parser, argv=argv)
    subcmd = func_kwargs.get('subcmd', None)
    if not subcmd:
        print(parser.format_help())
        return 0

    del func_kwargs['subcmd']
    funcs_dict = {f.__name__: f for f in funcs}
    return funcs_dict[subcmd](**func_kwargs)


_executors_mapping = {
    CMD: _execute_cmd,
    MULTI_CMD: _execute_multi_cmd,
    STREAM: _execute_stream,
}
