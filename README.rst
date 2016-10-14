==
hq
==
---------------------------------------------------------------------------------------------------------------------------------
hq is a powerful command-line tool for slicing and dicing HTML, then producing results as HTML, JSON or any other textual format.
---------------------------------------------------------------------------------------------------------------------------------

.. image:: https://travis-ci.org/rbwinslow/hq.svg?branch=master
    :target: https://travis-ci.org/rbwinslow/hq

hq is short for "HQuery," a query language combining XPath/XQuery and a smattering of original features such as interpolated strings and JSON construction, designed to pack as much flexibility and automation power as possible into a brief and expressive language optimized for use at the command line.

The remainder of this documentation assumes that you already know XPath_ (go check it out first, if you're unfamiliar), but you don't need any familiarity with XQuery to read on. So read on!

.. _XPath: https://www.w3.org/TR/xpath/


Why HQuery?
===========

HQuery includes XPath and borrows from XQuery, but it introduces new stuff, too, and even deviates in small ways from those standards. How come?

XPath seems counter-intuitive for a CLI because it's wordier than CSS selectors and less popular among Web developers, but its semantics are a superset of those in CSS and I wanted maximum querying power. My motivating examples included queries that couldn't be done as selectors without scripting logic. So I went with the ugly duckling and added non-standard features to make it less wordy (like abbreviated axes) and to borrow desirable features from CSS selectors (like the class axis).

XQuery_ is a functional programming language designed specifically for manipulating XML data. It's quite unpopular, even among developers who do a lot of work with XML, because it's wordy, obscure and laden with XML-ecosystem complexities like namespaces and a type system based on `XML Schemata`_. But I wanted power on the results-producing side of the picture as well, and XQuery has powerful features and semantics that are particularly well suited to the task. So HQuery borrows the simplest and most useful features from XQuery, decoupling them from those XML complexities and sprinkling them with some syntactic sugar to shorten things up a bit.

To top things off, HQuery adds a few original features, particularly interpolated strings, that enhance the language's ability to do really flexible querying, manipulation and output with very little syntax. Low investment, high yield. Don't you want to delete all that script code and turn it into just one expression on a command line, like jq_ allows you to do if you're crunching JSON? I know, I know, "Then I'll have `two problems`_."

.. _XQuery: https://www.w3.org/XML/Query/
.. _XML Schemata: https://www.w3.org/XML/Schema
.. _jq: https://stedolan.github.io/jq/
.. _two problems: https://blog.codinghorror.com/regular-expressions-now-you-have-two-problems/

Examples
--------

Consider some examples that illustrate what the language can do. These examples are all based on the contents of the Wikipedia (English) page for the first season of `Breaking Bad`_. The page contains a table of episodes that looks a little like this:

.. _Breaking Bad: https://en.wikipedia.org/wiki/Breaking_Bad_(season_1)

    +-----+-----------------------+----------------+----------------+
    | No. | Title                 | Director       | Writer         |
    +=====+=======================+================+================+
    | 1   | "Pilot"               | Vince Gilligan | Vince Gilligan |
    +-----+-----------------------+----------------+----------------+
    | Walter White, a 50-year-old chemistry teacher, secretly . . . |
    | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . |
    | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . |
    +-----+-----------------------+----------------+----------------+
    | 2   | "Cat's in the bag..." | Adam Bernstein | Vince Gilligan |
    +-----+-----------------------+----------------+----------------+
    | Walt and Jesse try to dispose of . . . . . . . . . . . . . .  |
    | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . |
    | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . |
    +---------------------------------------------------------------+

The real table has more columns than this, and the dots, here, are intended to signify a long paragraph of text (including spoilers!). Otherwise, this is a simple HTML ``table``, with ``tr`` rows and ``td`` cells.

Listing Directors
~~~~~~~~~~~~~~~~~

If all we want to do is list directors, one per line, the excellent CSS-based query tool pup_ can totally do the job:

.. _pup: https://github.com/ericchiang/pup

.. code-block:: bash

    curl -s 'https://en.wikipedia.org/wiki/Breaking_Bad_(season_1)' |
        pup '.wikiepisodetable tr:nth-child(even) td:nth-of-type(3) text{}' | uniq

I had to add a line break because of the long URL. From now on, let's just start these commands with ``curl_cmd |``.

The nice, terse ``pup`` script is just a CSS selector plus pup's ``text{}`` generator, which produces only the text content of HTML nodes instead of their full HTML representation. ``uniq`` deals with the duplicates (Adam Bernstein directed two episodes). The output looks like this::

    Vince Gilligan
    Adam Bernstein
    Jim McKay
    Tricia Brock
    Bronwen Hughes
    Tim Hunter

Can HQuery do any better? As it turns out, *not particularly*...:

.. code-block:: bash

    curl_cmd | hq '//.::wikiepisodetable//tr[even()]/td[3]//text()' | uniq

It's shorter, but it's maybe a little uglier (though beauty is in the eye of the beholder). There are clear parallels between the structure of the ``pup`` query and this one, but the syntax here is less familiar to Web developers. This example makes use of the abbreviated class axis feature and the ``even`` function in HQuery, which are helping to keep the command short but not doing too much to improve the aesthetics. If all I want to do is list these directors, and I'm not an XPath fanatic, then I probably don't give ``hq`` a second look.

Producing JSON
~~~~~~~~~~~~~~

What if we wanted to transform the episode records in this table into JSON? ``pup`` has a nice, terse ``json{}`` output transformer, like ``text{}``:

.. code-block:: bash

    curl_cmd | pup '.wikiepisodetable tr:nth-child(even) json{}'

``pup`` produces a general and very exhaustive JSON representation of the HTML markup, so this command produces almost six hundred lines of output. The first two cells from the HTML table come out looking like this:

.. code-block:: json

    {
        "tag": "td",
        "text": "1"
    },
    {
        "children": [
            {
                "href": "/wiki/Pilot_(Breaking_Bad)",
                "tag": "a",
                "text": "Pilot",
                "title": "Pilot (Breaking Bad)"
            }
        ],
        "class": "summary",
        "style": "text-align:left",
        "tag": "td",
        "text": "\u0026#34; \u0026#34;"
    },

The structure is starkly different between the two cells, because the actual markup looks different:

.. code-block:: html

    <td>1</td>
    <td class="summary" style="text-align:left">
        "<a href="/wiki/Pilot_(Breaking_Bad)" title="Pilot (Breaking Bad)">Pilot</a>"
    </td>

There are cells that deviate in other ways, including descendants two generations deep. Fortunately, there's another excellent tool, jq_, that does a superheroic job of slicing and dicing JSON, so it can consome this raw JSON and produce something more reasonable. Here's an expanded command making use of ``jq``:

.. _jq: https://stedolan.github.io/jq/

.. code-block:: bash

    curl_cmd | pup '.wikiepisodetable tr:nth-child(even) json{}' |
        jq 'map({number: .children[1].text, title: .children[2].children[0].text,
        director: (.children[3].text + .children[3].children[0].text),
        author: (.children[4].text + .children[4].children[0].text), aired: .children[5].text})'

I added line breaks for clarity, of course. The command produces nice JSON:

.. code-block:: json

    [
        {
            "number": "1",
            "title": "Pilot",
            "director": "Vince Gilligan",
            "author": "Vince Gilligan",
            "aired": "January 20, 2008"
        },

And so on...

The ``jq`` command is long but mostly readable. Even if you haven't used the tool or read the documentation, you can kind of tell from the curly braces and the attribute-like "name: expression" structure that most of the command is concerned with assembling the JSON hash for each episode. The longer expressions for "director" and "author" are needed because those cells sometimes contain hyperlinks with the names inside, sometimes not.

If the markup structure were more irregular than this, or we needed to deal with discontinuous text surrounding child elements (which ``pup``'s ``json{}`` generator wants to mash together), we might have a considerably more difficult time. But it's not! So far, so good.

How about ``hq``?

.. code-block:: bash

    curl_cmd | hq 'array { //.::wikiepisodetable//tr[even()] ->
        hash {number: $_/td[1], title: $_/td[2]/a, director: $_/td[3],
              author: $_/td[4], aired: $_/td[5]/text()}}'

Now we're starting to get somewhere. This solution is less code, uses one tool instead of two, and once you get the idea that there's an iteration going on here that's producing all of the hashes inside the array (that's what the ``->`` is doing), it's significantly easier to relate the JSON output to the HTML input. The repetitive '.children[#].children[#]' stuff obscures that relationship when we're chaining ``pup`` and ``jq``.

This example uses several features unique to ``hq``, including computed JSON array and hash construction, the abbreviated class axis and the abbreviated FLWOR iteration.

Adding Plot Summaries
~~~~~~~~~~~~~~~~~~~~~

Now things get interesting, because we're going to try to include the plot summaries from the episode table. As you may recall, those summaries are contained in separate rows, each following the row with the corresponding episode details in it.

Since ``pup`` is a pure query tool, and CSS selectors lack a means of representing "cousin" relationships, the only way to put these contents together is through the advanced functional programming features provided by ``jq``. There is probably more than one way to solve this problem in a powerful tool like ``jq``, but here's what I came up with:

.. code-block:: bash

    curl_cmd | jq 'reduce .[] as $row ([];
        if ($row.children | length) > 1 then
            . + [{no: $row.children[1].text, title: $row.children[2].children[0].text,
            director: ($row.children[3].text + $row.children[3].children[0].text),
            author: ($row.children[4].text + $row.children[4].children[0].text), aired: $row.children[5].text}]
        else last.plot = $row.children[0].text end)'

I've added line breaks and indentation to enhance clarity, obviously. This example uses ``jq``'s ``reduce`` and ``if-then-else`` syntax to build a new JSON array by adding episode details from episode rows, much as we were doing before, but stitching on the plot summaries rather than adding new array entries when we're iterating over a plot row (which we decide based on the number of cells in the row).

This solution has two problems, and one of them is a deal-breaker. That problem has to do with the presence of hyperlinks in the original HTML plot summaries. ``pup`` turned those hyperlinks into nested ``children`` array contents, stitching the remaining (non-hyperlink) text all together so that it's impossible to know where the hyperlink text was originally located in the overall cell text. Here's the HTML:

.. code-block:: html

    <td class="description" colspan="7" style="border-bottom:solid 3px #2FAAC3">
        Walter White, a 50-year-old chemistry teacher, secretly begins making crystallized
        <a href="/wiki/Methamphetamine" title="Methamphetamine">methamphetamine</a>
        to support his family after learning that he has terminal lung cancer. He teams up

        ... et cetera, et cetera ...
    </td>

For this ``td`` element, ``pup`` produces the following JSON:

.. code-block:: json

    {
        "children": [
        {
            "href": "/wiki/Methamphetamine",
            "tag": "a",
            "text": "methamphetamine",
            "title": "Methamphetamine"
        },
        {
            "href": "/wiki/Recreational_vehicle",
            "tag": "a",
            "text": "RV",
            "title": "Recreational vehicle"
        }
        ],
        "class": "description",
        "colspan": "7",
        "style": "border-bottom:solid 3px #2FAAC3",
        "tag": "td",
        "text": "Walter White, a 50-year-old chemistry teacher, secretly begins making
                 crystallized to support his family after learning that he has terminal
                 lung cancer. He teams up ... et cetera, et cetera ..."
    }

Notice how the word "methamphetamine" exists only in the ``children`` object representing the ``a`` tag that contained it in the HTML, and not after the word "crystallized" in the text that we are actually capturing in the command illustrated above. There's no way to put these back together again, and that's a deal breaker.

The other issue with this solution is its narrow applicability to JSON. ``jq`` happens to be an incredibly powerful tool, enabling this kind of manipulation logic because it's not just build for simple querying or reporting. But what if we were trying to solve this kind of problem with HTML as our input and some other representation as our output, like YAML or CSV or LaTeX or just differently structured HTML? As I mentioned above, we're already having to work with a data structure that is only indirectly tied to the original HTML, making our little script harder to read and relate to that content and also leading to fundamental limitations like the fragmented text problem we've run into.

To solve the immediate problem in ``hq``, we need only add one more clause to the hash:

.. code-block:: bash

    <curl_cmd> | jq 'array {//.::wikiepisodetable//tr[even()] -> hash {
        number: $_/td[1], title: $_/td[2]/a, director: $_/td[3],
        author: $_/td[4], aired: $_/td[5]/text(), plot: $_/>::tr[1]/td}}'

That very last hash key and value, ``plot: $_/>::tr[1]/td``, is all that was required to reach over into the next ``tr`` element (``>::`` is ``hq``'s abbreviated ``following-sibling`` axis, and the ``tr[1]`` part makes sure we get the first ``tr`` that follows the current one) and pluck out the text of its one-and-only ``td`` child. In this case, all of the plot text comes out unbroken, with the hyperlink text inserted in the right places, because ``hq``'s query and manipulation semantics are all based directly on HTML.

