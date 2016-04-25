#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Gr\xe9gory Operto'
SITENAME = u'Gr\xe9gory Operto'
SITEURL = ''
STATIC_PATHS = ['images', 'pdfs', 'widgets']
THEME = 'pure'

PATH = 'content'

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = ()

# Social widget
SOCIAL = ()

TWITTER_USERNAME = 'xgrg'
GITHUB_USERNAME = 'xgrg'
LINKEDIN_USERNAME = 'neuroimaging'
MENUITEMS = [('Home', '/'),
             ('Projects', '/projects/'),
             ('About', '/about/'),
             ]

DEFAULT_PAGINATION = 5
GOOGLE_ANALYTICS = 'UA-17275957-2'

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
