from os import linesep

from . import utils

LINES = 'lines'
CHARS = 'chars'
RAW = 'raw'

EXIT_OK = 0
EXIT_ERROR = 2

__all__ = (
    'get_input_parser', 'get_output_parser', 'LINES', 'CHARS', 'EXIT_OK',
    'EXIT_ERROR',
)


def get_input_parser(input_type):
    return _input_mapping[input_type]


def get_output_parser(output_type, input_type=None):
    # set output type same as input type when not specified
    output_type = output_type or input_type
    return _output_mapping[output_type]


def _input_lines(input_stream):
    for line in input_stream:
        yield line.rstrip(linesep)


def _input_chars(input_stream):
    char = input_stream.read(1)
    while char != '':
        yield char
        char = input_stream.read(1)


def _input_raw(input_stream):
    return input_stream


def _output_lines(output_stream, err_stream, output):
    return _output_writer(output_stream, err_stream, output, sep=linesep)


def _output_chars(output_stream, err_stream, output):
    return _output_writer(output_stream, err_stream, output, sep=None)


def _output_writer(output_stream, err_stream, output, sep):
    exitcode = EXIT_OK

    for outlines, err in output:
        # outlines can be iterable, str or None
        if outlines is None or isinstance(outlines, str):
            outlines = (outlines, )

        for outline in outlines:
            if outline is not None:
                output_stream.write(outline)
                if sep is not None:
                    output_stream.write(sep)

        if err is not None:
            err_stream.write(utils.error2str(err))
            if sep is not None:
                err_stream.write(linesep)
            exitcode = EXIT_ERROR

    return exitcode


_output_mapping = {
    None: _output_lines,
    LINES: _output_lines,
    CHARS: _output_chars,
    RAW: _output_chars,
}

_input_mapping = {
    None: _input_lines,
    LINES: _input_lines,
    CHARS: _input_chars,
    RAW: _input_raw,
}
