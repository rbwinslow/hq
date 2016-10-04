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

XPath is a very flexible path language for querying XML and (X)HTML documents, and it's not entirely unknown to Web developers. XQuery, on the other hand, is a not-very-popular functional programming language tightly focused around the task of manipulating XML data. It has very powerful features for solving problems in this space, but it's also too wordy, obscure and complex to appeal to developers in search of a low-investment/high-yield solution for HTML processing, which is what ``hq`` is intended to be. So I wondered how it might work out to just borrow the simplest and most useful features from XQuery, decoupled from XML complexities like namespaces and the schema-based type system, sprinkle on some syntactic sugar to shorten things up a bit, and maybe add a few features, particularly interpolated strings, to enhance the language's ability to build flexible output with very little syntax.

It worked out quite well, I think!

As an example, let's consider a problem involving the export of data embedded on a Web page in the form of a CSV_ file. The data are all of the episodes from the first season of Breaking Bad, the Web page is the season's Wikipedia_page_, and the CSV file that we want to produce is a little complicated because we want to include in every record a truncated plot "teaser" derived from the plot summaries in the episode table from the Web page. Each of those plot summaries in the Wikipedia episode table occupies its own entire row, right below the row where all of the other details for that episode sit. So the table on the Wikipedia page looks like this:

    +-----+-----------------------+----------------+----------------+
    | No. | Title                 | Director       | Writer         |
    +=====+=======================+================+================+
    | 1   | "Pilot"               | Vince Gilligan | Vince Gilligan |
    +-----+-----------------------+----------------+----------------+
    | Walter White, a 50-year-old chemistry teacher, secretly . . . |
    | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . |
    +-----+-----------------------+----------------+----------------+
    | 2   | "Cat's in the bag..." | Adam Bernstein | Vince Gilligan |
    +-----+-----------------------+----------------+----------------+
    | Walt and Jesse try to dispose of . . . . . . . . . . . . . .  |
    | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . |
    +---------------------------------------------------------------+

.. _CSV: http://edoceo.com/utilitas/csv-file-format
.. _Wikipedia_page: https://en.wikipedia.org/wiki/Breaking_Bad_(season_1)

The hyphen lines separate rows in the table, and the dots are intended to signify a long paragraph of text (including spoilers!). Now here is the kind of CSV output we're looking for::

    "No.","Title","Director","Writer","Plot Tease"
    "1","Pilot","Vince Gilligan","Vince Gilligan","Walter White, a 50-year-old chemistry..."
    "2","Cat's in the bag...","Adam Bernstein","Vince Gilligan","Walt and Jesse try to dispose of..."

Notice the "Plot Tease" column we've appended to the list of fields, and the truncated plot summary text that we've added to each CSV record. To produce such output, we need to query the page for the contents of the header row and each episode row in the episode table, as well as the interleaved rows containing just the plot summaries, we need to truncate the plot summaries, and we need to synthesize all of these contents into the CSV records depicted above, with the truncated plots following the other episode details in each record.

If you were using just an HTML query tool with no capability to assemble or synthesize outputs programmatically, you would have to write a script in your favorite scripting language to do this part of the work. In the XML world, you might find yourself solving such a problem in XQuery, in which case your solution might look something like this:

.. code-block:: xquery

    let $heads := (for $h in //tr[1]/th return concat('"', normalize-space($h), '",'), '"Plot Tease"')
    let $recs :=
        for $ep in //tr[position() mod 2 = 0]
        let $cols := for $col in $ep/* return concat('"', normalize-space($col), '",')
        let $plot := substring(normalize-space($ep/following-sibling::tr[1]/td), 1, 50)
        return concat("&#10;", string-join($cols), '"', $plot, '..."')
    return concat(string-join($heads), string-join($recs))

This is a relatively short and simplistic solution. It doesn't even truncate the plot summaries properly, at word boundaries, but instead just chops off at the fiftieth character and sticks on an ellipsis. Notice how wordy function calls like ``normalize-space``, the laborious ``concat`` and ``substring`` work, and even the verbose ``following-sibling`` XPath axis contribute to the overall length of this code sample.

If you're a sharp observer of XQuery code, you might suspect that we could lose the ``let $cols :=`` and even the ``let $heads :=`` lines altogether by collapsing them into the ``string-join`` calls later in the FLWOR, but there are line-breaking whitespaces in the original content that necessitate the ``normalize-space`` calls in these ``let`` declarations, so it's not so easy. If you're *not* a sharp observer of XQuery code, don't worry too much about the details; this sample is here just to illustrate the volume of code required to solve this problem in a language that was made for HTML-like data manipulation.

Here is the HQuery equivalent, with a few line breaks added for readability::

    concat(
        `"${j:","://.::wikiepisodetable/tr[1]/th}","Plot Tease"&#10;`,
        //.::wikiepisodetable/tr[position()mod2=0] -> `"${j:",":$_/*}","${t:50:...:$_/>::tr[1]/td}"&#10;`
    )

To me, this seems like a reasonable volume of code to pass along at the command-line to accomplish this task, while the XQuery sample above would not be. Here is a quick breakdown of this expression and the HQuery features on which it's based::

    `"${j:","://.::wikiepisodetable/tr[1]/th}","Plot Tease"&#10;`

This is where we put the table's column headings together, manufacturing the initial "header" record in the CSV output. The backticks at the beginning and end of this expression denote an interpolated string, a feature very popular among_ dynamic_ languages_ today. Here are some simpler examples of string interpolation in HQuery::

    1. `Variable x contains value $x`
    2. `Four plus four is ${4 + 4}`

.. _among: https://en.wikibooks.org/wiki/Ruby_Programming/Syntax/Literals#Interpolation
.. _dynamic: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Template_literals
.. _languages: http://docs.groovy-lang.org/latest/html/documentation/index.html#_string_interpolation

I should note that in HQuery, as in XQuery, all variable names begin with a dollar sign. When a simple variable name appears in an interpolated string, as in example (1), it will be replaced with its value, interpreted as a string. The "interpreted as a string" part is important, because XPath has very specific_rules_ about how node sets and other kinds of data are converted into strings, and HQuery adds the further step of normalizing_whitespace_ in those strings when they are derived from text content derived from the HTML document. This makes interpolated strings a nice shortcut for all of those ``normalize-space`` calls.

.. _specific_rules: https://www.w3.org/TR/xpath/#function-string
.. _normalizing_whitespace: https://developer.mozilla.org/en-US/docs/Web/XPath/Functions/normalize-space

As with interpolated strings found in other languages, you can use curly braces after the dollar sign to embed a more complicated expression in an interpolated string. This is illustrated in example (2) above, and it brings us back to what we see when we look inside the "headers" interpolated string. Let's break it up so we can talk about each piece::

    ` " ${j:",": //.::wikiepisodetable/tr[1]/th }  ","Plot Tease" &#10; `
     -- -------- ------------------------------ -- -------------- -----
     #1    #2                 #3                #2       #4        #5

The very first character, #1, is just the initial double quote that appears at the very beginning of the output.

#2 is an expression of the ``${<expr>}`` form embedded in the interpolated string, so it will be replaced with the evaluated result of the expression, converted to a string as necessary. But there's more going on at the beginning of this ``${}`` than just the dollar sign and the curly braces. That little colon-delimited clause at the beginning of the embedded expression, ``j:",":``, is called a *filter.*

Filters are a shorthand for various transformation functions that are useful to apply to the evaluated result of an embedded expression, and this is the "j" for "join" filter, which performs a string-join operation on the contents of a sequence (assuming the expression produces a sequence). The ``","`` argument between the colons is inserted between each item in the sequence that the join filter concatenates together.

#3 is the actual expression part of the embedded expression, and it looks *kind of like* a standard XPath, but a little different. The first location step in the path, ``.::wikiepisodetable``, utilizes a novel axis that HQuery adds to the set of standard XPath axes: the ``class`` axis. The ``class`` axis selects HTML elements whose ``class`` attribute contains the name in the name test part of the location step (which *has to* be a name test; you can't use a node test like ``node()`` here). Combined with the double-slash at the beginning of the path, this clause selects all of the elements in the entire HTML document that references the given CSS class name. On the *Breaking Bad* page, this matches the ``table`` element with all of the episodes in it.

I could also have written ``class::wikiepisodetable`` here instead, because the ``class`` axis (like other XPath axes) has an unabbreviated name, but the dot is shorter and reminiscent of class-based selection in CSS. HQuery provides abbreviated versions of all of the useful axes from XPath, but unlike XPath's own "@" shorthand for the ``attribute`` axis, all of these HQuery-proprietary abbreviations must be followed by the double-colon just to keep the parsing simple.

The remainder of this location path, ``tr[1]/th``, is all standard XPath. It selects all of the ``th`` element children inside the first ``tr`` element that's a child of the ``table`` selected in the first step. The location path produces, as a result, all of the header cells in the first row of the episode table. Combined with the join filter and the automatic string normalization HQuery performs on string values derived from HTML content, this succinctly constructs all of the header names with double quotes and commas in between.

#4 and #5 are both just more literal text included in the interpolated string, with #4 providing the last close double quote for the list of header names produced by the embedded expression as well as the extra heading for the "Plot Tease" column. #5 is an escape that adds a line feed at the end, getting us ready for the records produced by the second argument to the outer ``concat`` function call::

    //.::wikiepisodetable/tr[position()mod2=0] -> `"${j:",":$_/*}","${t:50:...:$_/>::tr[1]/td}"&#10;`

XQuery programmers (anybody there?) may not recognize this as an XQuery FLWOR_ statement, but that is what it is. The ``->`` operator is the HQuery iteration operator, and it maps to the semantics of XQuery FLWORs::

    <expr> -> <other-expr>  ::=  for $_ in <expr> return <other-expr>

.. _FLWOR: http://allthingsoracle.com/xquery-for-absolute-beginners-part-3-flwor/

As you might have guessed, XQuery background or no, this is a construct for iterating over the sequence of items produced by ``<expr>``, producing a new sequence composed of all of the results from evaluating ``<other-expr>`` on each iteration, with the item from ``<expr>`` being iterated over supplied to ``<other-expr>`` as a variable named ``$_``. With this overall structure in mind, let's start understanding this expression by deconstructing the expression that produces the items to be iterated over::

    //.::wikiepisodetable /tr [ position() mod 2 = 0 ]
    --------------------- --- ------------------------
              #1          #2            #3

We've already encountered #1 before; it selects the episode ``table`` element. #2 moves the selection down into the set of ``tr`` child elements inside the ``table``, but in this case we are selecting a different set of rows by using the all-standard-XPath predicate #3. This predicate causes us to select only those ``tr`` elements at even-numbered positions, ignoring both the header row (at position 1) and all of the plot summary rows (at positions 3, 5, 7, etc.). So this FLWOR is going to iterate over all of the row elements from the ``table`` that contain episode details. Now let's examine the other expression, where all the action is::

    -> `  "  ${j:",": $_/* }  "," ${t:50:...: $_/>::tr[1]/td  } "&#10;  `
       -- -- -------- ---- -- --- ----------- -------------- -- ------ --
       #1 #2    #3     #4  #3 #5      #6            #7       #6   #8   #1

#1 is the surrounding backticks that make this whole expression an interpolated string.

#2, like the double quote at the beginning of the previous interpolated string we just looked at, is just a literal double quote that's going to end up at the beginning of each record in the CSV output.

#3 is another embedded expression with a "join" filter just like the one we saw above, that stitched all of the headings together with surrounding double quotes and commas in between. This one is doing the same thing for all of the detail cells in the row we're iterating over, which are produced by the expression #4. In #4 we see our first use of the ``$_`` variable that the abbreviated FLWOR automatically declares, whose value is the ``tr`` element node surrounding all of the detail cells. Those cells are the only element children within that ``tr``, so the XPath is pretty simple: match all element children of the ``tr`` with ``/*``.

#5 is another static literal part of the string, inserting a comma and double quotes to separate the end of the details list from the last item in the record, the truncated "plot tease."

#6 is another embedded expression, this time using a filter we haven't seen: the "t" for "truncate" filter. Where the "join" filter accepted one colon-delimited argument, this one accepts two: a maximum length at which to truncate the string value of the embedded expression, and a string to use as a suffix at the end of the truncated string. This takes care of the plot tease truncation for us, and does so at a proper word boundary.

#7 is an expression that produces the plot summary corresponding to the details row in ``$_``. This XPath takes advantage of one of the abbreviated axes mentioned above: in this case, ``>::`` is used as an abbreviation for ``following-sibling::``. The rest of the expression is standard XPath, and it selects the one cell in the row that follows the details row in ``$_``.

#8, finally, is the last literal part of the interpolated string, consisting of a final double quote (to match the one before the plot tease) and a line feed, so that the next record will appear on a new line.
