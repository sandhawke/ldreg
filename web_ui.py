#!/home/ldreg/local/bin/python
###! /usr/bin/env python
"""

A Website which gives web users access to tracker functions.



At the moment, for development, this is just to run from the cmd line,
and it'll start web.py's web server.  There's a little wrapper code
needed in another file (dispatch.cgi, dispatch.fcgi) needed to make
this run as CGI/FastCGI.

"""


import sys
sys.path[0:0] = ('/home/sandro/ldreg/misc', )  # where html and webextras are
sys.path[0:0] = ('/home/ldreg/ldreg.net/misc', )  

import time

import web           # http://webpy.org 

from html import * # my toolkit...
import webextras

# import tracker

urls = (
  '/', 'Home',
  '/demo', 'Demo',
  '/statistics', 'Stats',
  '/blog', 'Blog',
  '/wiki', 'Wiki',
  '/about', 'About',

  '/find', 'Find',
  '/query', 'Query',
  '/register', 'Register',
  '/track', 'Track',


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

        self.footer << div(p("""DISCLAIMER: This is an experimental technology demonstration, being run as a hobby by Sandro Hawke (sandro@hawke.org).    It is not supported or endorsed by his employer at this time."""), id="disclaimer")
        
        #self.footer << p("Page generated in %f seconds." % (time.time()-self.t0))
        self.titlebar = div([], id="title")
        self.header << self.titlebar
        self.titlebar << h1("LD", em("Reg"))
        self.titlebar << h2("Linked Data Registration ", Raw("&mdash;"), " Now you can Query the Semantic Web")

        snul = ul()
        self.nav1 << snul
        for area in (Home(), Demo(), Stats(), Blog(), Wiki(), About()):
            if (area.__class__ == self.area.__class__ or
                area.__class__ == getattr(self.area, "parent", "").__class__):
                s=" active"
            else:
                s=""
            snul << li(a(area.label, href=get_url(area), class_="selectable"+s))

        # fill in nav2 in the cases where it's shown...
        if (self.area.__class__ == Home().__class__ or
            getattr(self.area, "parent", "").__class__ == Home().__class__):
            ul2 = ul()
            self.nav2 << div(ul2, class_="snav")
            for area in (Find(), Query(), Register(), Track()):
                if (area.__class__ == self.area.__class__):
                    s = " active"
                else:
                    s = ""
                ul2 << li(a(area.label, 
                            style="background:"+area.color+";",
                            href=get_url(area), 
                            class_="selectable"+s))

        
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
        page << p("@@@ Demos will go here, like 'Who Knows Me' and 'Lets See A Movie'")
        return page.done()

class Stats:

    label = "Stats"

    def GET(self):
        page = Page(self)
        page << p("@@@ Statistics should go here")
        return page.done()

class Blog:

    label = "Blog"

    def GET(self):
        page = Page(self)
        page << p("@@@ We don't have a blog yet.   So why is this page here?")
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

class Find:

    parent = Home()
    label = "Find"
    color = "#339999"
    
    def GET(self):

        page = Page(self)
        
        page << h2("Find Data Sources", style="background:"+self.color+"; padding: 1em;")
        page << p("@@@")
        return page.done()

class Query:

    parent = Home()
    label = "Query"
    color = "#006666"
    
    def GET(self):

        page = Page(self)
        page << h2("Query All Registered Data Sources", style="background:"+self.color+"; padding: 1em;")
        page << p("@@@")
        return page.done()

class Register:

    parent = Home()
    label = "Register"
    color = "#669966"
    
    def GET(self):

        page = Page(self)
        page << h2("Registered a Data Source", style="background:"+self.color+"; padding: 1em;")
        page << p("@@@")
        return page.done()

class Track:

    parent = Home()
    label = "Track"
    color = "#336633"
    
    def GET(self):

        page = Page(self)
        page << h2("Track Usage of a Vocabulary", style="background:"+self.color+"; padding: 1em;")

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


def cgiMain():   ########  CUT FROM SOMEWHERE ELSE AS EXAMPLE

    form = cgi.FieldStorage()
    source=form.getfirst("source")
    go=form.getfirst("go")
    if source is None or source == "":
        groupname = form.getfirst("group")
        group = local_groups_config.get_group(groupname)
        prompt(group)
    else:
        ensure_safety(source)
        if go == do_sync_msg:
            sync(source)
        else:
            # assume go == gen_preview_msg
            # because the old wiki pages don't tell us that.
            save = form.getfirst("save")
            if save is None or save == "":
                generate_page2(source)
            else:
                generate_page2(source, save=True, form=form)

##   # say that we're doing FCGI instead of just CGI
##   web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)


if __name__ == "__main__": 
    web.config.debug = True
    web.webapi.internalerror = web.debugerror
    app = web.application(urls, globals())
    app.run()
