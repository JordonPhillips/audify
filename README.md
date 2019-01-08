audify
======

A simple command line tool / python helper to convert a body of text to an mp3
using Amazon Polly. To use audify, you must first have AWS credentials set up.

Installation
------------

It is recommended to install audify using `pip`:

```
$ pip install audify
```

Examples
--------

The most common usage will be to pass in a simple text file and get the output:

```
$ echo "Hello World" > input.txt
$ audify -i input.txt -o output.mp3
```

You can also pass in text from stdin:

```
$ echo "Hello World" | audify -i - -o output.mp3
```

If you want to access audify from a Python script, you can import and call it
directly:

```python
from audify import audify

audify(
    input_filename='input.txt',
    output_filename='output.mp3',
)
```
You can also pass file-like objects:

```python
import io

from audify import audify_fileobj

audify_fileobj(
    fileobj=io.StringIO('Hello World'),
    output_filename='output.mp3',
)```

Any voice supported by Amazon Polly can be used:

```
$ echo "Hello World" | audify -i - -o output.mp3 -v Joey
```

```python
from audify import audify

audify(
    input_filename='input.txt',
    output_filename='output.mp3',
    voice='Ivy',
)```
