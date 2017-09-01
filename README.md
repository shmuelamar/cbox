# CBOX - CLI ToolBox

[![PyPI](https://img.shields.io/pypi/v/cbox.svg)](https://pypi.python.org/pypi/cbox/0.1.0)
[![PyPI](https://img.shields.io/pypi/pyversions/cbox.svg)](https://pypi.python.org/pypi/cbox/0.1.0)
[![Build Status](https://travis-ci.org/shmuelamar/cbox.svg?branch=master)](https://travis-ci.org/shmuelamar/cbox)
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
* concurrency (currently only threading)
* supports multiple types of pipe processing (lines, chars..)
* automatic docstring parsing for description and arguments help
* automatic type annotation and defaults parsing
* supports only python3 (yes this is a feature)

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

running it:

```bash
$ cat langs.txt | ./nth-line.py -n 1 | ./url-status.py 
http://python.org - 200
http://lisp-lang.org - 200
http://ruby-lang.org - 200
```


__more examples can be found on `examples/` dir__

## Contributing
cbox is an open source software and intended for everyone. please feel free to create PRs, add examples to examples/ dir, request features and ask questions.
