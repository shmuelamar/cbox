import argparse
import inspect
from argparse import ArgumentParser
import re

from cbox.exceptions import ArgumentException

_empty = inspect.Signature.empty

_DOCSTRING_REGEX = re.compile(r'^\s*\w.*?(\n\s*\n|$)', flags=re.DOTALL)
_DOCSTRING_PARAM_REGEX = re.compile(
    r'^\s*:param ([^:]*):([^:]*)$',
    flags=re.UNICODE | re.IGNORECASE | re.DOTALL | re.MULTILINE
)

__all__ = ('get_cli_parser', 'parse_args', )


def get_cli_parser(func, skip_first=0, parser=None):
    """makes a parser for parsing cli arguments for `func`.

    :param callable func: the function the parser will parse
    :param int skip_first: skip this many first arguments of the func
    :param ArgumentParser parser: bind func to this parser.
    """
    help_msg, func_args = _get_func_args(func)
    if not parser:
        parser = ArgumentParser(description=help_msg)

    for i, arg in enumerate(func_args):
        arg_name, arg_type, arg_default, arg_required, arg_help = arg
        if i < skip_first:
            continue

        if arg_default is not _empty:
            if arg[1] == bool:
                action = 'store_{}'.format(str(not arg_default).lower())
                parser.add_argument(
                    arg_name, default=arg_default,
                    required=arg_required, help=arg_help, action=action
                )
            else:
                parser.add_argument(
                    arg_name, type=arg_type, default=arg_default,
                    required=arg_required, help=arg_help
                )
        else:
            if arg[1] == bool:
                parser.add_argument(
                    arg_name, type=str2bool, required=arg_required, help=arg_help
                )
            else:
                parser.add_argument(
                    arg_name, type=arg_type, required=arg_required, help=arg_help
                )
    return parser


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1', 'True'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0', 'False'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_cli_multi_parser(funcs, skip_first=0):
    """makes a parser for parsing cli arguments for `func`.

    :param list funcs: the function the parser will parse
    :param int skip_first: skip this many first arguments of the func
    """
    parser = ArgumentParser(description='which subcommand do you want?')
    subparsers = parser.add_subparsers(
        title='subcommands', dest='subcmd', help=''
    )
    for func in funcs:
        help_msg, func_args = _get_func_args(func)
        sub_parser = subparsers.add_parser(func.__name__, help=help_msg)
        get_cli_parser(func, skip_first=skip_first, parser=sub_parser)
    return parser


def parse_args(parser, argv=None):
    cmd_kwargs = dict(parser.parse_args(argv).__dict__)
    return cmd_kwargs


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
        raise ValueError('parameter type %s is not yet supported' % param.kind)

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
