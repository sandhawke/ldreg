#! /usr/bin/env python
"""

  Can run as a web server OR on the command line.

      python tracker.py list 'http://ldreg.org/demo/pet-terms#Dog'

  Operations:
       scan -- tell the tracker about some source that may
                        have changed   
       list -- ask for a list of sources which use this term
       sync -- update a previous list of sources
       wait -- 

  Given the URL of some data source, register it with all appropriate
  trackers.

  ISSUE: can we do this anonymously, or do we need a relationship with
  the trackers?    I believe we can do it all anonymously.   


  FOR TESTING:
     -- need temp databases (memory?   scratch names?    scratch TABLES NAMES?)
     -- need web access over-ride?

"""

import sys
import urllib
import urllib2
import time

import scanner
import dbconn
import irimap
import splitter

def scan(source):   
    """Go see what's going on at this source and update the database
    based on changes it may have had.

    We just use our scanner, but under the cover it can/should use an
    public delegation to other scanners.


    """
    db = dbconn.Connection()
    scanner.ensure_scanned(db, source)

def latest_timecode(db):
    for r in db.query("select id from scan order by id desc limit 1"):
        return r.id

class GarbageTimecode ( Exception ):
    pass

def min_timecode(db):
    v = 0
    for r in db.query("select val from globals where prop='min_timecode'"):
        v = int(r.val)
    return v

def list_(term, timecode=(-1), db=None):   # , limit, offset):
    """

    see http://dev.mysql.com/doc/refman/5.0/en/select.html

    for us, timecodes ARE scanids.   A new scanid == a new change.

    are we going to need to SORT when we do limit/offset?   pagerank?

    """
    if db is None:
        db = dbconn.Connection()

    (ns, local) = splitter.split(term)
    ns_id = irimap.to_id(db, ns)

    if timecode == -1:
        timecode = latest_timecode(db)
        print "list using latest timecode:", timecode
    else:
        if timecode < min_timecode(db):
            raise GarbageTimecode()

    for r in db.query('select text, type from term_use, scan, iri where scan_id <= $timecode and obsoleted_by > $timecode and namespace_id=$ns_id and scan.id=scan_id and status=1 and local=$local and iri.id=source_id', vars=locals()):
        yield unicode(r.type)+" "+unicode(r.text)

def sync(term, start_timecode, stop_timecode):
    """
    Report back on the additions and deletions to the list for this
    term between the two timecodes.  Should be rejected if we've garbage
    collected them timecodes, but that should usually only happen if
    the changes are enough that list() is faster anyway.
    """
    db = dbconn.Connection()
    old = sorted(list_(term, start_timecode, db))
    new = sorted(list_(term, stop_timecode, db))
    (dels, adds) = diff(old, new)
    scanner.vote_timecode(db, term, start_timecode, stop_timecode,
                          useful=( len(dels) + len(adds) < len(new) ))
    return (dels, adds)   
    #for x in dels:
    #    print "-",x
    #for x in adds:
    #    print "+",x

def wait(term, after_timecode):
    """Wait until there's a change in the list for term after the
    given timecode.

    Obviously our notion of 'waiting' depends on our concurrency
    environment.

    """


    raise Exception('not implemented yet')

def diff(old, new):
    deleted = []
    added = []
    i = 0
    j = 0
    while i < len(old):
        if j >= len(new):
            deleted.extend(old[i:])
            break
        if old[i] == new[j]:
            i += 1
            j += 1
        elif old[i] < new[j]:
            deleted.append(old[i])
            i += 1
        else: #  old[i] > new[j]:
            added.append(new[j])
            j += 1
    while j < len(new):
            added.append(new[j])
            j += 1
    return (deleted, added)
    
def watch(term):
    
    last = []
    while True:
        new = sorted(list_(term))
        (dels, adds) = diff(last, new)
        for x in dels:
            print "-",x
        for x in adds:
            print "+",x
        last = new
        time.sleep(0.5)

    
################################################################

import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import define, options

class Tracker(tornado.web.RequestHandler):
    def get(self):

        # allow term to be wildcarded...?
        # specify ROLE, along with term?

        op = self.get_argument("op", "manual")
        if op == "manual":
            self.write("<p>No manual mode yet, sorry.</p>")
        elif op == "scan":
            source = self.get_argument("source")
            scan(source)
            self.ok()
        elif op == "list":
            term = self.get_argument("term")
            tc = int(self.get_argument("timecode", "-1"))
            for s in list_(term, tc):
                self.write(s+"\n")  # use json?
        elif op == "sync":
            term = self.get_argument("term")
            tc0 = int(self.get_argument("start"))
            tc1 = int(self.get_argument("stop", "-1"))
            (dels, adds) = sync(term, tc0, tc1)
            self.write("del "+repr(dels))
            self.write("add "+repr(adds))
        elif op == "source-status":
            source = self.get_argument("source")
            # should report the last-modified for that source.
        else:
            raise tornado.web.HTTPError(404, "Invalid op value %s" %`op`)

    def post(self):

        op = self.get_argument("op", "manual")
        if op == "scan":
            source = self.get_argument("source")
            scan(source)
            self.ok()

    def ok(self):
        self.set_header("Content-Type", "text/plain")
        self.write("200 OK\n")

            

def web_main():
    define("port", default=8088, help="run on the given port", type=int)
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/", Tracker),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

################################################################


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "scan":
            scan(sys.argv[2])
            print "done."
        elif sys.argv[1] == "list":
            try:
                tc = sys.argv[3]
            except IndexError:
                tc = -1
            for s in list_(sys.argv[2], tc):
                print s
        elif sys.argv[1] == "watch":
            watch(sys.argv[2])
        elif sys.argv[1] == "sync":
            sync(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
        elif sys.argv[1] == "serve":
            web_main()

if __name__ == "__main__": 
    main()

