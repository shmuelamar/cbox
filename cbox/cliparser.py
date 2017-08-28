import inspect
from argparse import ArgumentParser

import re

_empty = inspect.Signature.empty

_DOCSTRING_REGEX = re.compile(r'^\s*\w.*?(\n\s*\n|$)', flags=re.DOTALL)
_DOCSTRING_PARAM_REGEX = re.compile(
    r'^\s*:param ([^:]*):([^:]*)$',
    flags=re.UNICODE | re.IGNORECASE | re.DOTALL | re.MULTILINE
)

__all__ = ('get_cli_parser', 'parse_args', 'resolve_func', )


def get_cli_parser(func, skip_first=1):
    """TBD"""
    help_msg, func_args = _get_func_args(func)
    parser = ArgumentParser(description=help_msg)

    for i, arg in enumerate(func_args):
        arg_name, arg_type, arg_default, arg_required, arg_help = arg
        if i < skip_first:
            continue

        if arg_default is not _empty:
            parser.add_argument(
                arg_name, type=arg_type, default=arg_default,
                required=arg_required, help=arg_help
            )
        else:
            parser.add_argument(
                arg_name, type=arg_type, required=arg_required, help=arg_help
            )
    return parser


def parse_args(parser, argv=None):
    """TBD"""
    cmd_kwargs = dict(parser.parse_args(argv).__dict__)
    return cmd_kwargs


def resolve_func(func=None, modulename='funcs_example'):
    # TODO: import from environ and default home folder path
    # TODO: ensure path import works
    if callable(func):
        return func

    modulename = modulename  # TODO: preprocess this
    funcname = func.replace('-', '_')
    module = __import__(modulename)
    return getattr(module, funcname)


def _get_func_args(func):
    func_args = []

    sig = inspect.signature(func)
    help_msg, doc_params = _parse_docstring(func.__doc__)

    for param in sig.parameters.values():
        func_args.append(_param2args(param, doc_params.get(param.name)))

    return help_msg, func_args


def _strip_lines(txt):
    lines = []
    for line in txt.splitlines():
        line = line.strip()
        if line:
            lines.append(line)
    return '\n'.join(lines)


def _parse_docstring(docstring):
    """parses docstring into its help message and params"""
    params = {}

    if not docstring:
        return None, params

    try:
        help_msg = _DOCSTRING_REGEX.search(docstring).group()
        help_msg = _strip_lines(help_msg)
    except AttributeError:
        help_msg = None

    for param in _DOCSTRING_PARAM_REGEX.finditer(docstring):
        param_definition = param.group(1).rsplit(' ', 1)
        if len(param_definition) == 2:
            param_type, param_name = param_definition
        else:
            param_type = None
            param_name = param_definition[0]

        param_help = param.group(2).strip()
        params[param_name] = param_type, _strip_lines(param_help)
    return help_msg, params


def _param2args(param, doc_param=None):
    if param.kind != param.POSITIONAL_OR_KEYWORD:
        # TODO: exception Hirarchy
        raise Exception('this type of param not yet supported')

    arg_name = '%s%s' % ('--' if len(param.name) > 1 else '-', param.name.replace('_', '-'))  # noqa
    arg_required = param.default is _empty
    arg_default = param.default
    arg_help = doc_param[1] if doc_param else None

    if param.annotation is not _empty:
        arg_type = param.annotation
    elif param.default is not None and param.default is not _empty:
        arg_type = type(param.default)
    else:
        arg_type = str

    return arg_name, arg_type, arg_default, arg_required, arg_help
