# CBOX - CLI ToolBox

[![PyPI](https://img.shields.io/pypi/v/cbox.svg)](https://pypi.python.org/pypi/cbox/0.1.0)
[![PyPI](https://img.shields.io/pypi/pyversions/cbox.svg)](https://pypi.python.org/pypi/cbox/0.1.0)
[![Build Status](https://travis-ci.org/shmuelamar/cbox.svg?branch=master)](https://travis-ci.org/shmuelamar/cbox)
[![AppVeyor](https://img.shields.io/appveyor/ci/gruntjs/grunt.svg)](https://ci.appveyor.com/project/shmuelamar/cbox)
[![Codecov](https://img.shields.io/codecov/c/github/shmuelamar/cbox.svg)](https://codecov.io/gh/shmuelamar/cbox)
[![PyPI](https://img.shields.io/pypi/wheel/cbox.svg)]()
[![PyPI](https://img.shields.io/pypi/l/cbox.svg)]()

### convert any python function to unix-style command

The Unix Philosophy (from [wikipedia](https://en.wikipedia.org/wiki/Unix_philosophy#Origin)):
>    * *Write programs that do one thing and do it well.*
>    * *Write programs to work together.*
>    * *Write programs to handle text streams, because that is a universal interface.*

<br />

## Features
* supports pipes
* concurrency (threading or asyncio)
* supports error handling (redirected to stderr)
* supports for inline code in cli style
* various output processing options (filtering, early stopping..)
* supports multiple types of pipe processing (lines, chars..)
* automatic docstring parsing for description and arguments help
* automatic type annotation and defaults parsing
* returns the correct exitcode based on errors
* supports only python3 (yes this is a feature)
* supports subcommands

## Quickstart

**install:**

```bash
pip install -U cbox
```

**example usage:**
```python
#!/usr/bin/env python3
# hello.py
import cbox

@cbox.cmd
def hello(name: str):
    """greets a person by its name.

    :param name: the name of the person
    """
    print(f'hello {name}!')

if __name__ == '__main__':
    cbox.main(hello)
```

**run it:**

```bash
$ ./hello.py --name world
hello world!

$ ./hello.py --help
usage: hello.py [-h] --name NAME

greets a person by its name.

optional arguments:
  -h, --help   show this help message and exit
  --name NAME  the name of the person
```

**cli inline example:**

```bash
$ echo -e "192.168.1.1\n192.168.2.3\ngoogle.com" | cbox --modules re 're.findall("(?:\d+\.)+\d+", s)'
192.168.1.1
192.168.2.3
```

*for more info about cbox inline run `cbox --help`*


## The Story
once upon a time, a python programmer named dave, had a simple text file. 

**langs.txt**
```text
python http://python.org
lisp http://lisp-lang.org
ruby http://ruby-lang.org
```

all dave wanted is to get the list of languages from that file.

our dave heard that unix commands are the best, so he started googling them out.

he started reading about *awk*, *grep*, *sed*, *tr*, *cut* and others but couldn't 
remember how to use all of them - after all he is a python programmer and wants to use python.

fortunately, our little dave found out about **`cbox`** - a simple way to convert 
any python function into unix-style command line!

now dave can process files using python easily!

### simple example
```python
#!/usr/bin/env python3
# first.py
import cbox

@cbox.stream()
def first(line):
    return line.split()[0]

if __name__ == '__main__':
    cbox.main(first)
```

running it:

```bash
$ cat langs.txt | ./first.py 
python
lisp
ruby
```

**or inline cli style:**

```bash
$ cat langs.txt | cbox 's.split()[0]'
```

*note: **`s`** is the input variable*


now dave is satisfied, so like every satisfied programmer - he wants more!

dave now wants to get a list of the langs urls.

### arguments and help message

```python
#!/usr/bin/env python3
# nth-item.py
import cbox

@cbox.stream()
# we can pass default values and use type annotations for correct types
def nth_item(line, n: int = 0):
    """returns the nth item from each line.

    :param n: the number of item position starting from 0
    """
    return line.split()[n]

if __name__ == '__main__':
    cbox.main(nth_item)
```

running it:

```bash
#!/usr/bin/env python3
$ ./nth-item.py --help
usage: nth-item.py [-h] [-n N]

returns the nth item from each line.

optional arguments:
  -h, --help  show this help message and exit
  -n N        the number of item position starting from 0
```

```bash
$ cat langs.txt | ./nth-item.py 
python
lisp
ruby
```

```bash
$ cat langs.txt | ./nth-item.py -n 1
http://python.org
http://lisp-lang.org
http://ruby-lang.org
```

now dave wants to get the status out of each url, for this we can use `requests`.

but to process a large list it will take too long, so he better off use threads.

### threading example

```python
#!/usr/bin/env python3
# url-status.py
import cbox
import requests

@cbox.stream(worker_type='thread', max_workers=4)
def url_status(line):
    resp = requests.get(line)
    return f'{line} - {resp.status_code}'

if __name__ == '__main__':
    cbox.main(url_status)
```

**running it:**

```bash
$ cat langs.txt | ./nth-line.py -n 1 | ./url-status.py 
http://python.org - 200
http://lisp-lang.org - 200
http://ruby-lang.org - 200
```

**or inline cli style**

```bash
$ cat langs.txt | cbox 's.split()[1]' | cbox -m requests  -w thread -c 4 'f"{s} - {requests.get(s).status_code}"'
http://python.org - 200
http://lisp-lang.org - 200
http://ruby-lang.org - 200
```


## Advanced Usage
### Error handling

```python
#!/usr/bin/env python3
# numbersonly.py
import cbox

@cbox.stream()
def numbersonly(line):
    """returns the lines containing only numbers. bad lines reported to stderr.
    if any bad line is detected, exits with exitcode 2.
    """
    if not line.isnumeric():
        raise ValueError('{} is not a number'.format(line))
    return line

if __name__ == '__main__':
    cbox.main(numbersonly)
```

all errors are redirected to `stderr`:

```bash
$ echo -e "123\nabc\n567" | ./numbersonly.py
123
Traceback (most recent call last):
  File "/home/shmulik/cs/cbox/cbox/concurrency.py", line 54, in _simple_runner
    yield func(item, **kwargs), None
  File "numbersonly.py", line 11, in numbersonly
    raise ValueError('{} is not a number'.format(line))
ValueError: abc is not a number

567

```

we can ignore the `stderr` stream by redirecting it to `/dev/null`:
```bash
$ echo -e "123\nabc\n567" | ./numbersonly.py 2>/dev/null
123
567
```

our command returns 2 as the [exit code](https://en.wikipedia.org/wiki/Exit_status#Shell_and_scripts), 
indicating an error, we can get the last error code by running `echo $?`:

```bash
$ echo $?
2
```

### Filtering

`cbox.stream` supports three types of return values - `str`, `None` and `iterable` of `str`s.

`None` skips and outputs nothing, `str` is outputted normally and each item in the `iterable` is treated as `str`.

here is a simple example:

```python
#!/usr/bin/env python3
# extract-domains.py
import re
import cbox

@cbox.stream()
def extract_domains(line):
    """tries to extract all the domains from the input using simple regex"""
    return re.findall(r'(?:\w+\.)+\w+', line) or None  # or None can be omitted

if __name__ == '__main__':
    cbox.main(extract_domains)
```

we can now run it (notice that we can have multiple domains or zero domains on each line):
```bash
$ echo -e "google.com cbox.com\nhello\nfacebook.com" | ./extract-domains.py 
google.com
cbox.com
facebook.com
```

### Early Stopping
`cbox.stream` supports early stopping, i.e. stopping before reading the whole `stdin`

example implementing a simple `head` command
```python
#!/usr/bin/env python3
# head.py
import cbox

counter = 0


@cbox.stream()
def head(line, n: int):
    """returns the first `n` lines"""
    global counter
    counter += 1

    if counter > n:
        raise cbox.Stop()  # can also raise StopIteration()
    return line


if __name__ == '__main__':
    cbox.main(head)
```

getting the first 2 lines:

```bash
$ echo -e "1\n2\n3\n4" | ./head.py -n 2
1
2
```


### Concurrency

`cbox` supports **simple (default)**, **asyncio** and **thread** workers. we can use asyncio like this:

```python
#!/usr/bin/env python3
# tcping.py
import asyncio
import cbox

@cbox.stream(worker_type='asyncio', workers_window=30)
async def tcping(domain, timeout: int=3):
    loop = asyncio.get_event_loop()

    fut = asyncio.open_connection(domain, 80, loop=loop)
    try:
        reader, writer = await asyncio.wait_for(fut, timeout=timeout)
        writer.close()
        status = 'up'
    except (OSError, asyncio.TimeoutError):
        status = 'down'

    return '{} is {}'.format(domain, status)

if __name__ == '__main__':
    cbox.main(tcping)
```

this will try open up to 30 connections in parallel using asyncio. 

running it:

```bash
$ echo -e "192.168.1.1\n192.168.2.3\ngoogle.com"  | ./tcping.py
192.168.1.1 is down
192.168.2.3 is down
google.com is up
```

__more examples can be found on `examples/` dir__

## Contributing
cbox is an open source software and intended for everyone. please feel free to create PRs, add examples to examples/ dir, request features and ask questions.

### Creating Local Dev Env

after cloning the repo, you'll need to install test dependencies from `test-requirements.txt`.

there is a simple `make` command to install them (you'll need [`miniconda`](https://conda.io/miniconda.html) installed):

```bash
$ make test-setup
```

or you can use `pip install -r test-requirements.txt` (preferably in new virtualenv).

now ensure all tests passes and runs locally:

```bash
$ make test
```
