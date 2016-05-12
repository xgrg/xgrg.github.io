#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Gr\xe9gory Operto'
SITENAME = u'Gr\xe9gory Operto'
SITEURL = ''
STATIC_PATHS = ['images', 'pdfs', 'widgets', 'js']
THEME = 'pure'
DISPLAY_CATEGORIES_ON_MENU = False
DISPLAY_PAGES_ON_MENU = False
FILENAME_METADATA = '(?P<date>\d{4}-\d{2}-\d{2})-(?P<slug>.*)'
DIRECT_TEMPLATES = ('index', 'archives')
ARCHIVES_SAVE_AS = 'archives/index.html'
ARTICLE_URL = '{slug}/'
ARTICLE_SAVE_AS = '{slug}/index.html'
PAGE_URL = '{slug}/'
PAGE_SAVE_AS = '{slug}/index.html'
TAG_URL = 'tag/{slug}/'
TAG_SAVE_AS = 'tag/{slug}/index.html'
TAGS_SAVE_AS = ''
AUTHOR_URL = ''
AUTHOR_SAVE_AS = ''
CATEGORY_URL = ''
CATEGORY_SAVE_AS = ''

PATH = 'content'
DATE_FORMATS = {
    'en': '%Y-%m-%d',
}
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
             ('About', '/about/'),
             ]

DEFAULT_PAGINATION = 5
GOOGLE_ANALYTICS = 'UA-17275957-2'
DISQUS_SITENAME = 'xgrg'


# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
