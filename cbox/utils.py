import traceback
from io import StringIO

__all__ = ('error2str', )


def error2str(e):
    """returns the formatted stacktrace of the exception `e`.

    :param BaseException e: an exception to format into str
    :rtype: str
    """
    out = StringIO()
    traceback.print_exception(None, e, e.__traceback__, file=out)
    out.seek(0)
    return out.read()
