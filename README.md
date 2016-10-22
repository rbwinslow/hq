# hq
**Powerful HTML slicing and dicing in the form of a console tool**

[![Build Status](https://travis-ci.org/rbwinslow/hq.svg?branch=master)](https://travis-ci.org/rbwinslow/hq) [![Coverage Status](https://coveralls.io/repos/github/rbwinslow/hq/badge.svg?branch=master)](https://coveralls.io/github/rbwinslow/hq?branch=master)

`hq` is a Python-based command-line tool for querying HTML and producing results as HTML, JSON or any other textual format. Pass `hq` an expression written in its compact, flexible HQuery expression language, along with an HTML file, and it will find the content you're seeking, shape it and emit it in whatever form you want.

HQuery, the little language in `hq`, is based on [XPath](https://www.w3.org/TR/xpath/), and is compliant with the XPath 1.0 standard, minus some features not applicable to HTML. That's nice for querying, but you need more power to take control of the shape and format of the data you produce. To that end, HQuery also includes...

* **Nuggets of XQuery** &mdash; only a few of the good parts! Just enough for iteration, branching and the like.
* **XPath expansions for HTML** &mdash; including a `class::` axis and `class()` function to simplify querying with CSS classes.
* **Super-charged string interpolation** &mdash; with powerful filters that you can chain together to transform data as you produce it.
* **Computed constructors for HTML and JSON** &mdash; so you can programmatically assemble and output new HTML or JSON objects and arrays.

## Installing `hq`

    pip install hq
    
*Needle scratch sound...* Oh, wait! I haven't actually released 0.0.1 yet! So it's not uploaded. You'll have to clone the repo and run the `hq_runner.py` script in place of `hq` until a release is up.

## Running `hq`

    cat /path/to/file.html | hq '`Hello, ${/html/head/title}`!'

...or...

    hq -f /path/to/file.html '`Hello, ${/html/head/title}`!'
    
To print usage information:

    hq --help

## Learning `hq`

The [wiki](https://github.com/rbwinslow/hq/wiki) discusses the [motivations](https://github.com/rbwinslow/hq/wiki/Why-HQuery%3F) guiding the HQuery language's design and provides a [language reference](https://github.com/rbwinslow/hq/wiki/Language-Reference).

## Contributing to `hq`

`hq` is tested against Python 2.7 and recent generations of Python 3 (3.4 and 3.5, as of this writing). The file structure and `setup.py` script for the project are based on [this blog post](https://gehrcke.de/2014/02/distributing-a-python-command-line-application/).

`hq`'s dependencies are split into a "base" file, the subset needed to run the application, and a "dev" file providing the tools necessary to run tests and the like. To do development:

    pip install -r requirements/dev.txt

### Running Tests

    py.test
    
If you want to turn verbosity on, you need the `--gabby` flag. You'll probably also want to run just one test at a time, because `--gabby` is way gabby:

    py.test --gabby -vv -k some_particular_test_function
