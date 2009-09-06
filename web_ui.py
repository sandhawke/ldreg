#! /usr/bin/env python
"""

A Website which gives web users access to tracker functions.



At the moment, for development, this is just to run from the cmd line,
and it'll start web.py's web server.  There's a little wrapper code
needed in another file (dispatch.cgi, dispatch.fcgi) needed to make
this run as CGI/FastCGI.

"""


import sys
sys.path[0:0] = ('/home/sandro/ldreg/misc', )  # where html and webextras are

import time

import web           # http://webpy.org 

from html import * # my toolkit...
import webextras

import tracker



urls = (
  '/', 'Home',
  '/demo', 'Demo',
  '/stats', 'Stats',
  '/blog', 'Blog',
  '/wiki', 'Wiki',
  '/about', 'About',

  '/register', 'Register',
  '/status', 'Status',
  '/search', 'Search',
  '/(.*\.(?:js|css|html|JPG))', 'static',
  '/test(.*)', 'test',
  '/dump', 'dump',
  '/(.*)', 'notfound',
  )

def get_url(handler):
    for i in range(0, len(urls), 2):
        if urls[i+1] == handler.__class__.__name__:
            return urls[i]
    raise RuntimeException('no url for '+handler.__class__.__name__)

class Page:

    '''

    nav1     highest level nav
    nav2     next level nav
                   (which we'll assemble on the side for now...)
    sidebar == right side, column 3

    doctree?    eh...   that's nav2.

    '''

    def __init__(self, area=None, title=None):
        self.t0 = time.time()
        self.area = area
        self.title = title
        self.doc = Document()

        # this is how the CSS thinks of them
        self.header =  div(' ', id="header")
        self.col1   =  div(' ', class_='col1')
        self.col2   =  div(' ', class_='col2')
        self.col3   =  div(' ', class_='col3')
        self.footer =  div(' ', id="footer")

        # but in general, I want to think of them like this.
        self.main   =  self.col1
        self.nav1   =  div(' ', class_='nav1 nav')
        self.nav2   =  self.col2
        self.sidebar=  self.col3


    def __lshift__(self, content):
       """Convenience syntax for append, with no parens to balance."""
       return self.main << content

    def done(self):

        self.footer << div(p("""DISCLAIMER: This is an experimental technology demonstration, being run by Sandro Hawke (sandro@hawke.org) as a hobby.    It is not supported or endorsed by his employer at this time."""), id="disclaimer")
        
        #self.footer << p("Page generated in %f seconds." % (time.time()-self.t0))
        self.titlebar = div([], id="title")
        self.header << self.titlebar
        self.titlebar << h1("LD", em("Reg"))
        self.titlebar << h2("Linked Data Registration ", Raw("&mdash;"), " Now you can Query the Semantic Web")

        snul = ul()
        self.nav1 << snul
        for area in (Home(), Demo(), Stats(), Blog(), Wiki(), About()):
            if area.__class__ == self.area.__class__:
                s=" active"
            else:
                s=""
            snul << li(a(area.label, href=get_url(area), class_="selectable"+s))

        
        web.expires(60)
        web.header('Content-Type', 'text/html; charset=utf-8')
        if self.title is None:
            self.title = "LDReg: "+self.area.label
        self.doc.head << title(self.title)
        self.doc.head << link(rel="stylesheet", type="text/css", href="/tables.css")
        self.doc.head << link(rel="stylesheet", type="text/css", href="/black.css")

        
        self.doc << self.header
        self.header << self.nav1

        d3 = div(self.col1, self.col2, self.col3, class_="colleft")
        self.doc << div(div(d3, class_="colmid"),
                        class_="colmask threecol")

        self.doc << self.footer
        return self.doc

class static:
    def GET(self, filename):
        return webextras.serveStatic(filename)

class Home:

    label = "Home"

    def GET(self):
        page = Page(self)
        page << p("@@@ to do")
        return page.done()

class Demo:

    label = "Demo"

    def GET(self):
        page = Page(self)
        page << p("@@@ to do")
        return page.done()

class Stats:

    label = "Stats"

    def GET(self):
        page = Page(self)
        page << p("@@@ to do")
        return page.done()

class Blog:

    label = "Blog"

    def GET(self):
        page = Page(self)
        page << p("@@@ to do")
        return page.done()

class Wiki:

    label = "Wiki"

    def GET(self):
        page = Page(self)
        page << p("This page should never be seen, due to apache config.")
        return page.done()


class About:

    label = "About"

    def GET(self):

        page = Page(self)
        page << p("This website is maintained by Sandro Hawke (sandro@hawke.org) as an experiment.")
        page << p("Although Sandro is an MIT employee and a staff member at W3C, this work is not endorsed by, supported by, funded by, or in way offically connected with either MIT or W3C.")
        return page.done()

class Register:

    def GET(self):

        page = Page("Register")
        page << p("@@@")
        return page.done()

class Status:

    def GET(self):

        page = Page("Status")
        page << p("@@@")
        return page.done()

class Search:

    def GET(self):

        try:
            item = web.input().item
        except AttributeError:
            item = None

        page = Page("Search")

        if item is None or item == "":
            comment = ""
        else:
            comment = self.do_search(page, item)
            if comment is None:
                return page.done()

        f = form("Data Source:")
        if comment:
            f << div("* ", comment, class_="error")
        f << input(value=item, type="text", name="item", size="80")
        f << " "
        f << input(type="submit", value="Submit")
        page << f

        return page.done()

    def do_search(self, page, iri):
        if not iri.startswith("http://"):
            return "URL does not start with http://..."
        page << "Search results..."
        
        for row in tracker.nfind(iri):
            page << p("Row:", `row`)
  

    POST=GET


class notfound:

    def GET(self, name):
        return webextras.notFound(name)

class dump:

    def GET(self):
        raise RuntimeError('Dump Called')

if __name__ == "__main__": 
    web.config.debug = True
    web.webapi.internalerror = web.debugerror
    app = web.application(urls, globals())
    app.run()
