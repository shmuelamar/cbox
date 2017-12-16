import inspect
from argparse import ArgumentParser
import re

_empty = inspect.Signature.empty

_DOCSTRING_REGEX = re.compile(r'^\s*\w.*?(\n\s*\n|$)', flags=re.DOTALL)
_DOCSTRING_PARAM_REGEX = re.compile(
    r'^\s*:param ([^:]*):([^:]*)$',
    flags=re.UNICODE | re.IGNORECASE | re.DOTALL | re.MULTILINE
)

__all__ = ('get_cli_parser', 'parse_args', )


class Arg:
    def __init__(
            self, type_=str, positional=False, names=None, help_=None):
        self.names = names
        self.type_ = type_
        self.positional = positional
        self.help_ = help_

    def get_names(self):
        if self.positional:
            return self.names

        return list(map(lambda _: ('--' if len(_) > 1 else '-') + _,
                    self.names))


def get_cli_parser(func, skip_first=0):
    """makes a parser for parsing cli arguments for `func`.

    :param callable func: the function the parser will parse
    :param int skip_first: skip this many first arguments of the func

    """
    help_msg, func_args = _get_func_args(func)
    parser = ArgumentParser(description=help_msg)

    for arg in func_args[skip_first:]:
        arg_type, arg_default, arg_required = arg

        kwargs = {
            'type': arg_type.type_,
            'default': None if arg_default is _empty else arg_default,
            'required': arg_required,
            'help': arg_type.help_,
        }

        if arg_type.positional:
            kwargs.pop('required')
            kwargs['nargs'] = '?'

        parser.add_argument(*arg_type.get_names(), **kwargs)

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
    """parses docstring into its help message and params."""
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

    arg_required = param.default is _empty
    arg_default = param.default

    if param.annotation is not _empty:
        arg_type = param.annotation
    elif param.default is not None and param.default is not _empty:
        arg_type = type(param.default)
    else:
        arg_type = str

    if not isinstance(arg_type, Arg):
        arg_type = Arg(type_=arg_type)

    if arg_type.names is None:
        arg_type.names = [param.name.replace('_', '-')]

    if arg_type.help_ is None:
        arg_type.help_ = doc_param[1] if doc_param else None

    return arg_type, arg_default, arg_required
