from os import linesep

LINES = 'lines'
CHARS = 'chars'
RAW = 'raw'

__all__ = ('get_input_parser', 'get_output_parser', 'LINES', 'CHARS', )


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


def _output_lines(output_stream, output):
    for line in output:
        output_stream.write(line)
        output_stream.write(linesep)


def _output_chars(output_stream, output):
    for char in output:
        output_stream.write(char)


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
