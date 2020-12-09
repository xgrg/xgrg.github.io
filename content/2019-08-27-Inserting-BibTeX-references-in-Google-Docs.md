Title: Working with academic references in Google Docs
Category: XNAT
Status: Published
Tags: bibtex, academia
Authors: Grégory Operto

We are still hoping for an era where citation management software would be free,
interoperable, easy to use and nicely integrated with word processing tools.

<!-- PELICAN_END_SUMMARY -->


Until this dream comes true, we need practical solutions.
BibTeX is a standard format used by most citation managing systems and initially
 designed to work with LaTeX. Working with LaTeX allows multiple users to jointly
  work on a same manuscript using a version control system e.g `git`. In line with
   this, LaTeX writers may now opt for several recently emerged online real-time
    editing platforms ([Overleaf](http://overleaf.com)), allowing to collaborate on the source and
     instantly visualize the compiled result. In parallel, other tools such as
      (Open/Libre/Microsoft) Office have seen developing plugins to allow
      inserting references from BibTeX (or other) files, offering a popular
      alternative for non-LaTeX non-git users.

Finally, Google Docs users do not have much option here, as the only existing
plugin to work with references in Google Docs comes as a paid service with
[Paperpile](http://paperpile.com). Hence this post describes a kind of recipe intended for Google Docs
users wanting to work with BibTeX references in a shared document.

Consider for example a document including BibTeX reference ID (here preceded by
`@`, as in `@Author2019`). By taking as inputs the document ID and a BibTeX
bibliography source file featuring the cited references, this technique will
generate a copy of the document having all reference ID replaced by, either a
reference number or a mention such as `First Author et al. (2019)`.
It will also compile a full list of the used references to get included e.g. at
the end of the document.

The core idea is based on making calls to the Google API from a Python app to
apply the right changes to the document. Getting started takes 3 steps:

- download the Python app/script
- enable the Google API and obtain client credentials
- look up the ID of a document and pass it to the app along with the corresponding .bib file.

The app will generate a copy of the document with initial reference ID replaced
by their full version as given by the `.bib` file.

`bibtex2docs.py DOCUMENT_ID BIBTEX_FILE CREDENTIALS`

![example1](https://gitlab.com/xgrg/bibtex2docs/raw/master/doc/example1.png)

![example2](https://gitlab.com/xgrg/bibtex2docs/raw/master/doc/example2.png)

![example3](https://gitlab.com/xgrg/bibtex2docs/raw/master/doc/example3.png)

![example4](https://gitlab.com/xgrg/bibtex2docs/raw/master/doc/example4.png)

More information at [http://gitlab.com/xgrg/bibtex2docs](http://gitlab.com/xgrg/bibtex2docs).

Install with `pip install bibtex2docs` .
