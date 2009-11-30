#! /usr/bin/env python
"""


  Given the URL of some data source, register it with all appropriate
  trackers.

  ISSUE: can we do this anonymously, or do we need a relationship with
  the trackers?    I believe we can do it all anonymously.   

  TODO:
      have a version of this that doesn't use a database, so it's
      easier for folks to install on their local system.

"""

import sys
import urllib
import urllib2

import scanner

def register(source):
    """ A while-you-wait registration function.

    As an ideal web service, this should enqueue all the notifies

       db.insert(reqg, tracker_id, source_id, when_added)

    so they can be batched, and we can monitor to outgoing
    notification queue, etc.   Also, if we're running that 
    tracker, we could just handle it under the covers.
    """

    print "Registering ", source
    ns_list = determine_namespaces(source)

    trackers = {}
    for ns in ns_list:
        if not ns: continue
        print "Finding trackers for ns", `ns`
        ns_trackers = determine_trackers(ns)
        for t in ns_trackers:
            trackers.setdefault(t, []).append(ns)

    print
    for (t,t_ns_list) in trackers.items():
        if not t: continue
        print "Notifying", `t`
        notify(t, source, t_ns_list)
    print "regdone."

def determine_namespaces(source):
    """Return a list of the namespaces used in the data at this
    source.    

    Talk to local scanner, or use the web to talk to the source's
    scanner?  Nah, in any case use our own scanner, which may talk to
    the source's scanner.
    """
    return scanner.scan(source).split("\n")

def determine_trackers(ns):
    """Return a list of the tracker iris for this namespace.  Primary
    first, if there is one, I guess.

    Maybe we can/should extend the scanner to do this?

    .../namespaces?source=___
    .../trackers?source=___    [it derefs the namespaces]
    
    nah, that's our job...

    store in db:    (namespace, tracker, is_primary)

    (but how often to do we need to refresh that?)

    HACK FOR NOW: just use the scanner, until we factor out its
    triple streaming and caching code....
    """
    return scanner.trackers(ns).split("\n")

def notify(tracker, source, namespaces):
    """Notify this tracker that this source now uses (only) these namespaces

    (Do we need to pass the namespaces?  Does the tracker care??  It
    might allow the tracker to work better.)
    """

    # is the tracker URL the same as the tracker POST address?  I guess so!

    values = {'op': 'scan',
              'source' : source,
              'namespaces' : " ".join(namespaces),
              }

    data = urllib.urlencode(values)
    req = urllib2.Request(tracker, data)   # headers?
    response = urllib2.urlopen(req)
    the_page = response.read()
    print "the_page", the_page


def main():
    if len(sys.argv) > 1:
        register(sys.argv[1])
    else:
        web_main()

if __name__ == "__main__": 
    main()

