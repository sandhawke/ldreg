#! /usr/bin/env python
"""

  Can run as a web server OR on the command line.

      python tracker.py list 'http://ldreg.org/demo/pet-terms#Dog'

  Operations:
       ping -- tell the tracker about some source that may
                        have changed
       list -- ask for a list of sources which use this term
       sync -- update a previous list of sources
       wait -- 

  Given the URL of some data source, register it with all appropriate
  trackers.

  ISSUE: can we do this anonymously, or do we need a relationship with
  the trackers?    I believe we can do it all anonymously.   

"""

import sys
import urllib
import urllib2

import scanner
import dbconn
import irimap
import splitter

def ping(source):   
    """Go see what's going on at this source and update the database
    based on changes it may have had.

    We just use our scanner, but under the cover it can/should use an
    public delegation to other scanners.

    rename as "scan" ?

    """
    db = dbconn.Connection()
    scanner.ensure_scanned(db, source)

def list(term):  # todo: , timecode, limit, offset):
    """

    see http://dev.mysql.com/doc/refman/5.0/en/select.html

    for us, timecodes ARE scanids.   A new scanid == a new change.
    """
    db = dbconn.Connection()
    (ns, local) = splitter.split(term)
    ns_id = irimap.to_id(db, ns)
    
    # will include obsolete scans, maybe...?   or is that status=2?
    # (or do we need to bring timecodes into that?)
    for r in db.query('select text from term_use, scan, iri where namespace_id=$ns_id and scan.id=scan_id and status=1 and local=$local and iri.id=source_id', vars=locals()):
        yield r.text

def sync(term, after_timecode, through_timecode):
    """
    Report back on the additions and deletions to the list for this
    term between the two timecodes.  Will be rejected if we've garbage
    collected them timecodes, but that should usually only happen if
    the changes are enough that list() is faster anyway.
    """

    raise Exception('not implemented yet')


def wait(term, after_timecode):
    """Wait until there's a change in the list for term after the
    given timecode.

    Obviously our notion of 'waiting' depends on our concurrency
    environment.

    """


    raise Exception('not implemented yet')


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "ping":
            ping(sys.argv[2])
            print "done."
        elif sys.argv[1] == "list":
            for s in list(sys.argv[2]):
                print s
        elif sys.argv[1] == "serve":
            web_main()

if __name__ == "__main__": 
    main()

