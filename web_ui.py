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



urls = (
  '/', 'Main',
  '/main', 'Main',
  '/about', 'About',
  '/register', 'Register',
  '/status', 'Status',
  '/search', 'Search',
  '/(.*\.(?:js|css|html|JPG))', 'static',
  '/test(.*)', 'test',
  '/dump', 'dump',
  '/(.*)', 'notfound',
  )


class Page:

    def __init__(self, area=None, title=None):
        self.t0 = time.time()
        self.area = area
        self.title = title
        self.doc = Document()
        
        self.header =  div(' ', id="header")
        self.sitenav = div(' ', id="sitenav")
        self.doctree = div(' ', id="doctree")
        self.sidebar = div(' ', id="sidebar")
        self.main =    div(' ', id="main")
        self.footer =  div(' ', id="footer")

    def __lshift__(self, content):
       """Convenience syntax for append, with no parens to balance."""
       return self.main << content

    def done(self):

        self.footer << div(hr(), p("""DISCLAIMER: This is an experimental service, being run as a hobby.    Contact Sandro Hawke (sandro@hawke.org) for more information.  Although Sandro is an MIT employee and a staff member at W3C, this work is not endorsed by, supported by, funded by, or in any way offically connected with either MIT or W3C.  So don't ask me about it during the work day, and don't suggest that LDReg is a W3C product!"""), id="disclaimer")
        
        # self.footer << p("Page generated in %f seconds." % (time.time()-self.t0))
        self.header << h1("LD", em("Reg"))

        snul = ul()
        self.sitenav << snul
        for area in ("Main", "Search", "Register", "Status", "About"):
            if area.lower() == self.area.lower():
                s=" selected"
            else:
                s=""
            snul << li(a(area, href="/"+area.lower()), class_="selectable"+s),

        
        web.expires(60)
        web.header('Content-Type', 'text/html; charset=utf-8')
        if self.title is None:
            self.title = "LDReg: "+self.area
        self.doc.head << title(self.title)
        self.doc.head << link(rel="stylesheet", type="text/css", href="/tables.css")
        self.doc.head << link(rel="stylesheet", type="text/css", href="/site.css")
        self.doc << self.header
        self.doc << self.sitenav
        self.doc << self.doctree
        self.doc << self.sidebar
        self.doc << self.main
        self.doc << self.footer
        return self.doc

class static:
    def GET(self, filename):
        return webextras.serveStatic(filename)

class Main:
    
    def GET(self):
        page = Page("Main")
        page << h2('ldreg!')
        page << p("@@@ to do")
        page << p("This technology is under development.  There is no stable published specification at this time.")
        return page.done()

class About:

    def GET(self):

        page = Page("About")
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

        page = Page("Search")
        page << p("@@@")
        return page.done()

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
