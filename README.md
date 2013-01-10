docx2html
=========

Convert a docx (OOXML) file to html

Usage
=====

    >>> from docx2html import convert
    >>> html = convert('path/to/docx/file')


Running Tests
=============

    $ ./run_tests.sh


Description
===========

docx2html is designed to take a docx file and extract the content out and
convert that content to html. It does not care about styles or fonts or
anything that changes how the content is displayed (with few exceptions). Below
is a list of what currently works:

* Paragraphs
    * Bold
    * Italics
    * Underline
    * Hyperlinks
* Lists
    * Nested lists
    * List styles (letters, roman numerals, etc.)
* Tables
    * Rowspans
    * Colspans
    * Nested tables
    * Lists
* Images
    * Resizing
    * Converting to smaller formats (for bitmaps and tiffs)
    * There is a hook to allow setting the src of the image tag out of context,
      more on this later
* Headings
    * Simple headings
    * Root level lists that are upper case roman numerals get converted to h2
      tags
