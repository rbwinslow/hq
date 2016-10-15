==
hq
==
---------------------------------------------------------------------------------------------------------------------------------
hq is a powerful command-line tool for slicing and dicing HTML, then producing results as HTML, JSON or any other textual format.
---------------------------------------------------------------------------------------------------------------------------------

.. image:: https://travis-ci.org/rbwinslow/hq.svg?branch=master
    :target: https://travis-ci.org/rbwinslow/hq

hq is short for "HQuery," a query language combining XPath/XQuery and a smattering of original features such as interpolated strings and JSON construction, designed to pack as much flexibility and automation power as possible into a brief and expressive language optimized for use at the command line.

The remainder of this documentation assumes that you already know XPath_ (go check it out first, if you're unfamiliar), but you don't need any familiarity with XQuery to read on.

.. _XPath: https://www.w3.org/TR/xpath/

The first section, *Why HQuery,* presents some examples comparing ``hq`` to similar solutions for querying HTML and producing various kinds of output. This is intended to illustrate the unique value of the ``hq`` approach, so if you just want to start using ``hq``, you might skip this first section and go straight to the next one, _`Running hq`.

Why HQuery?
===========

HQuery, the little, proprietary query language in ``hq``, includes XPath and borrows from XQuery, but it introduces new stuff, too, and even deviates in small ways from those standards. How come?

XPath seems counter-intuitive for a CLI because it's wordier than CSS selectors and less popular among Web developers, but its semantics are a superset of those in CSS and I wanted maximum querying power. My motivating examples included queries that couldn't be done as selectors without scripting logic. So I went with the ugly duckling and added non-standard features to make it less wordy (like abbreviated axes) and to borrow desirable features from CSS selectors (like the class axis).

XQuery_ is a functional programming language designed specifically for manipulating XML data. It's quite unpopular, even among developers who do a lot of work with XML, because it's wordy, obscure and laden with XML-ecosystem complexities like namespaces and a type system based on `XML Schemata`_. But I wanted power on the results-producing side of the picture as well, and XQuery has powerful features and semantics that are particularly well suited to the task. So HQuery borrows the simplest and most useful features from XQuery, decoupling them from those XML complexities and sprinkling them with some syntactic sugar to shorten things up a bit.

.. _XQuery: https://www.w3.org/XML/Query/
.. _XML Schemata: https://www.w3.org/XML/Schema

To top things off, HQuery adds a few original features, particularly interpolated strings, that enhance the language's ability to do really flexible querying, manipulation and output with very little syntax. Low investment, high yield. Don't you want to delete all that script code and turn it into just one expression on a command line, like jq_ allows you to do if you're crunching JSON? I know, I know, "Then I'll have `two problems`_."

.. _jq: https://stedolan.github.io/jq/
.. _two problems: https://blog.codinghorror.com/regular-expressions-now-you-have-two-problems/

By way of illustration, let's consider some examples that illustrate what the language can do. These examples are all based on the contents of the Wikipedia (English) page for the first season of `Breaking Bad`_. The page contains a table of episodes that looks a little like this:

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
-----------------

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

It's shorter, but it's maybe a little uglier (though beauty is in the eye of the beholder). There are clear parallels between the structure of the ``pup`` query and this one, but the syntax here is less familiar to Web developers. This example makes use of the abbreviated class axis feature and the ``even()`` function in HQuery, which are helping to keep the command short but not doing too much to improve the aesthetics. If all I want to do is list these directors, and I'm not an XPath fanatic, then I probably don't give ``hq`` a second look.

Producing JSON
--------------

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

``hq`` Solution
~~~~~~~~~~~~~~~

Now we start to see how ``hq`` can provide a more streamlined solution:

.. code-block:: bash

    curl_cmd | hq 'array { //.::wikiepisodetable//tr[even()] ->
        hash {number: $_/td[1], title: $_/td[2]/a, director: $_/td[3],
              author: $_/td[4], aired: $_/td[5]/text()}}'

This is less code, uses one tool instead of two, and once you get the idea that there's an iteration going on here that's producing all of the hashes inside the array (that's what the ``->`` is doing), it's significantly easier to relate the JSON output to the HTML input. The repetitive '.children[#].children[#]' stuff that obscured that relationship when we were chaining ``pup`` and ``jq`` is all gone.

This example uses several features unique to ``hq``, including computed JSON array and hash construction, the abbreviated class axis and the abbreviated FLWOR iteration.

Adding Plot Summaries
---------------------

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

Broken Solution
~~~~~~~~~~~~~~~

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

The other issue with this solution is its narrow applicability to JSON. ``jq`` happens to be an incredibly powerful tool, enabling this kind of manipulation logic because it's not just built for simple querying or reporting. But what if we were trying to solve this kind of problem with HTML as our input and some other representation as our output, like YAML or CSV or LaTeX or just differently structured HTML? As I mentioned above, we're already having to work with a data structure that is only indirectly tied to the original HTML, making our little script harder to read and relate to that content and also leading to fundamental limitations like the fragmented text problem we've run into.

``hq`` to the Rescue
~~~~~~~~~~~~~~~~~~~~

To solve the immediate problem in ``hq``, we need only add one more clause to the hash:

.. code-block:: bash

    curl_cmd | jq 'array {//.::wikiepisodetable//tr[even()] -> hash {
        number: $_/td[1], title: $_/td[2]/a, director: $_/td[3],
        author: $_/td[4], aired: $_/td[5]/text(), plot: $_/>::tr[1]/td}}'

That very last hash key and value, ``plot: $_/>::tr[1]/td``, is all that was required to reach over into the next ``tr`` element (``>::`` is ``hq``'s abbreviated ``following-sibling`` axis, and the ``tr[1]`` part makes sure we get the first ``tr`` that follows the current one) and pluck out the text of its one-and-only ``td`` child. In this case, all of the plot text comes out unbroken, with the hyperlink text inserted in the right places, because ``hq``'s query and manipulation semantics are all based directly on HTML.

Producing a CSV File
--------------------

What if our end goal wasn't JSON, but some other format like CSV_ (useful for exporting data to spreadsheets, among other applications)? Using other tools like ``pup`` and ``jq``, we're going to have to do most of the work in some other scripting language, like a ``bash`` script or Python. ``jq`` isn't really useful for this task, as it was designed to output only JSON, and its considerable flexibility and power is almost all focused on structured JSON manipulation rather than string manipulation.

.. _CSV: http://edoceo.com/utilitas/csv-file-format

Here's a naive but readable ``bash`` script that uses ``pup`` to extract individual chunks of text from the Web page and assembles them into a CSV format:

.. code-block:: bash

    curl -s 'https://en.wikipedia.org/wiki/Breaking_Bad_(season_1)' >bb.html

    echo -n '"'
    for i in 1 2 3 4 5 6 7
    do
        cell=`cat bb.html | pup ".wikiepisodetable tr:nth-child(1) th:nth-child($i) text{}"`
        if [ $i -gt 1 ]
        then
            echo -n '","'
        fi
        echo -n ${cell//[[:space:]]+/ }
    done
    echo '","Plot"'

    row=2
    while [ 1 ]
    do
        cell=`cat bb.html | pup ".wikiepisodetable tr:nth-child($row) th:nth-child(1) text{}"`
        if [ -z "$cell" ]
        then
            break
        fi
        echo -n "\"$cell"

        for i in 2 3 4 5 6 7
        do
            if [ $i = 3 ]
            then
                extra="a"
            else
                extra=
            fi

            cell=`cat bb.html | pup ".wikiepisodetable tr:nth-child($row) td:nth-child($i) $extra text{}"`
            echo -n '","'
            echo -n ${cell//[[:space:]]+/ }
        done

        echo -n '","'
        cell=`cat bb.html | pup ".wikiepisodetable tr:nth-child($((row+1))) td:nth-child(1) text{}"`
        echo -n ${cell//[[:space:]]+/ }
        echo '"'

        row=$(( row + 2 ))
    done

The output CSV includes a header row, containing the names of the columns derived from the ``th`` cells in the first row of the table, as well as the plot summaries from the odd-numbered rows, added onto each record as the last field. There's some special treatment for a couple of columns due to structural issues like the double quotes around episode title hyperlinks and the fact that the first column takes the form of ``th`` rather than ``td`` cells.

As I mentioned previously, most of the work here is being done by our own shell script rather than ``pup``. One undesirable side-effect of this division of labor is the need to store the HTML file on the file system and read it (and parse it) once for every single field value in the CSV output.

XQuery Diversion
~~~~~~~~~~~~~~~~

Even with XQuery, which is a powerful language specifically designed to query and manipulate HTML-like data, the solution to this problem is not a tiny block of code:

.. code-block:: xquery

    let $heads := (for $h in //tr[1]/th return concat('"', normalize-space($h), '",'), '"Plot Tease"')
    let $recs :=
        for $ep in //tr[position() mod 2 = 0]
        let $cols := for $col in $ep/* return concat('"', normalize-space($col), '",')
        let $plot := normalize-space($ep/following-sibling::tr[1]/td)
        return concat("&#10;", string-join($cols), '"', $plot, '"')
    return concat(string-join($heads), string-join($recs))

This code is actually quite a bit shorter than it would have been if written in plain vanilla XQuery 1.0, as it takes advantage of the more recently added ``string-join`` function to shorten some otherwise laborious string handling logic. Nevertheless, it's not the sort of thing you would want to pass as a parameter on the command line, which is what ``hq`` is all about. And in any case, we can't use XQuery because the input is HTML, not XML.

The ``hq`` Solution
~~~~~~~~~~~~~~~~~~~

Here's what a single ``hq`` command looks like to produce the same CSV output:

.. code-block:: bash

    curl_cmd | hq 'let $t := //.::wikiepisodetable return
        concat(`"${j:",":$t/tr[1]/th}","Plot"&#10;`,
        $t/tr[even()] -> `"${rr:":::j:",":$_/*}","${$_/>::tr[1]/td}"&#10;`)'

I've broken the line up a bit, of course, but you can see how all of this fits more or less comfortably on a single command line.

On the first line, I'm assigning the episode table element to a variable because it's a long location path and I'm going to use it twice. Users of XQuery will recognize the ``let`` and ``return`` as a FLWOR expression.

On the second line, I'm calling the ``concat()`` function, which concatenates strings, and I'm passing the finished CSV header line as its first argument. That header line comes in the form of an interpolated string (surrounded by backticks, like JavaScript 6 interpolated strings) in which I use ``hq``'s "join" filter (the ``j:",":`` part) to stitch all of the text from the ``th`` elements in the first row with double quotes and commas in between. I also add the "Plot" heading and a line feed (in the form of the HTML entity ``&#10;``) at the end.

On the third line, I use an abbreviated FLWOR expression (signified by the arrow ``->``) to iterate through all of the even-numbered table rows (the ones with the episode details in them), and for each row I produce an interpolated string that embeds two expressions (``${...}``, just like in JavaScript), the first one evaluating to all of the episode detail text from the elements row joined together (using the ``j:",":`` "join" filter again) and the second injecting the plot summary from the next row, which it fetched with ``hq``'s abbreviated "next sibling" axis, ``>::``. In an abbreviated FLWOR, ``hq`` provides the current node being iterated over in the variable ``$_``, so the expression ``$_/*`` produces all of the ``td`` children under the current ``tr`` row I'm iterating over, and the ``j:<delimiter>:`` filter takes the string values of all of those ``td`` elements (i.e., all text contained within, recursively and in the right order) and joins them with double quotes and commas in between.

There's another filter there, too: the "regex replace" filter, ``rr:<find-pattern>:<replace-pattern>:<flags>:``. The regular expression syntax is Python's, and in this case I'm using it to remove unwanted double quotes surrounding cell values, which is actually a problem only with ``td``s in the *Title* column (see the HTML markup above, under _`Producing JSON`). It seems like more colons than you might ideally want when you're just purging double quotation marks, but it's a very general tool.

I should note how these filters are chained together: they operate against the embedded expression value in sequence from left to right (which might seem counterintuitive from a functional programming perspective), and the regex replace filter will perform its replacement on the string values of all of the items in a sequence when the value of the expression is a sequence. So first the regex replace filter emits a sequene of quotation-mark-stripped strings derived from the original ``td`` elements, and then the join filter stitches them all into one string with the commas and double quotes in between.

Bonus
~~~~~

There's another intriguing filter that is applicable to this use case, that being the "truncate" or ``tru:<limit>:<suffix>:`` filter. True to its name, the ``tru:::`` filter cuts a string short at a certain size if the string is longer, but it does so at the last word (whitespace) boundary within that length limit, and it adds a suffix of your choosing at the end of any string it truncates. We can use this to gracefully chop down those plot summaries and give them a sense of mystery:

.. code-block:: bash

    curl_cmd | hq 'let $t := //.::wikiepisodetable return
        concat(`"${j:",":$t/tr[1]/th}","Plot"&#10;`,
        $t/tr[even()] -> `"${rr:":::j:",":$_/*}","${tru:50:...:$_/>::tr[1]/td}"&#10;`)'

    "No. overall","No. in season","Title","Directed by","Written by","Original air date","U.S. viewers (millions)","Plot"
    "1","1","Pilot","Vince Gilligan","Vince Gilligan","January 20, 2008 (2008-01-20)","1.41[3]","Walter White, a 50-year-old chemistry teacher,..."
    "2","2","Cat's in the Bag...","Adam Bernstein","Vince Gilligan","January 27, 2008 (2008-01-27)","1.49[4]","Walt and Jesse try to dispose of the two bodies..."

Tough for the ``bash`` script, kind of tough for the XQuery script (no built-in word break function), but a snap in ``hq``. Want a filter to solve a problem? E-mail me! Or do some tinkering in ``string_interpolation.py`` and initiate a pull request.

Running hq
==========


