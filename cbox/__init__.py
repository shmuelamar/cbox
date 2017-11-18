__description__ = 'convert any python function to unix-style command'
__version__ = '0.4.0'
__author__ = 'Shmuel Amar'
__url__ = 'https://github.com/shmuelamar/cbox'
__license__ = 'MIT'
__keywords__ = 'unix command pipes cli'

from .cli import stream, cmd, main  # noqa
from .concurrency import Stop  # noqa
