# hq
**Powerful HTML slicing and dicing at the command line.**

[![Build Status](https://travis-ci.org/rbwinslow/hq.svg?branch=master)](https://travis-ci.org/rbwinslow/hq) [![Coverage Status](https://coveralls.io/repos/github/rbwinslow/hq/badge.svg?branch=master)](https://coveralls.io/github/rbwinslow/hq?branch=master)

`hq` is a Python-based command-line tool for querying HTML, manipulating data and producing results as HTML, JSON or any other format. It's based on a compact, flexible expression language that started out as an XPath implementation but ended up going a few different places, so I'm going ahead and calling it HQuery.

HQuery is 99% compliant with the [XPath 1.0](https://www.w3.org/TR/xpath/) standard, minus some features not applicable to HTML. That's nice for querying, but you need more power to take control of the shape and format of the data you produce. To that end, HQuery also includes...

* **Nuggets of XQuery** &mdash; only a few of the good parts! Just enough for iteration, branching and the like.
* **XPath expansions for HTML** &mdash; including a `class::` axis and `class()` function, plus abbreviated axes to keep things terse.
* **Super-charged string interpolation** &mdash; with powerful filters that you can chain together to transform data as you produce it.
* **Computed constructors for HTML and JSON** &mdash; so you can programmatically assemble and output new HTML or JSON objects and arrays.
* **Out-of-left-field union decomposition** &mdash; enabling amazingly terse and powerful mappings from clauses in a union to different expressions.

## Installing `hq`

    pip install hq

## Running `hq`

    cat /path/to/file.html | hq '`Hello, ${/html/head/title}!`'

...or...

    hq -f /path/to/file.html '`Hello, ${/html/head/title}!`'
    
To print usage information:

    hq --help

## Learning `hq`

The [wiki](https://github.com/rbwinslow/hq/wiki) discusses the [motivations](https://github.com/rbwinslow/hq/wiki/Why-HQuery%3F) guiding the HQuery language's design and provides a [language reference](https://github.com/rbwinslow/hq/wiki/Language-Reference).

## Contributing to `hq`

`hq` is tested against Python 2.7 and recent generations of Python 3 (3.4 and 3.5, as of this writing). The file structure and `setup.py` script for the project are based on [this blog post](https://gehrcke.de/2014/02/distributing-a-python-command-line-application/).

`hq`'s dependencies are split into a "base" file, the subset needed to run the application, and a "dev" file providing the tools necessary to run tests and the like. To do development:

    pip install -r requirements/dev.txt

The parsing logic in `hquery_processor.py` is based on the [top-down operator precendence](https://www.crockford.com/javascript/tdop/tdop.html) approach.

### Running Tests

    py.test
    
The "dev.txt" dependencies also include [pytest-cov](https://pypi.python.org/pypi/pytest-cov), so you can generate a nice coverage report (which you'll find in the `htmlcov` directory):

    py.test --cov=hq --cov-report html
    
If you want to turn verbosity on to figure out what's going on in a test, you need the `--gabby` flag (since `py.test` owns its own `-v` flag). You'll probably also want to run just one test at a time, because `--gabby` is way gabby:

    py.test --gabby -vv -k some_particular_test_function
