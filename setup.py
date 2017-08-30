import re
from os.path import dirname, abspath, join

from setuptools import setup

HERE = dirname(abspath(__file__))
NAME = 'cbox'
META_FILE_PATH = join(HERE, NAME, '__init__.py')

REQUIREMENTS = []
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3 :: Only',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Intended Audience :: Information Technology',
    'Operating System :: OS Independent',
]


def readme():
    with open('README.md') as f:
        return f.read()


with open(META_FILE_PATH) as fp:
    META_FILE = fp.read()


def find_meta(meta):
    """
    Extract __*meta*__ from META_FILE.
    """
    meta_match = re.search(
        r'^__{meta}__ = [\'"]([^\'"]*)[\'"]'.format(meta=meta), META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError('Unable to find __{meta}__ string.'.format(meta=meta))


setup(
    name=NAME,
    version=find_meta('version'),
    description=find_meta('description'),
    long_description=readme(),
    classifiers=CLASSIFIERS,
    keywords=find_meta('keywords'),
    url=find_meta('url'),
    author=find_meta('author'),
    license=find_meta('license'),
    packages=[NAME],
    install_requires=REQUIREMENTS,
    include_package_data=True,
    zip_safe=False,
)
