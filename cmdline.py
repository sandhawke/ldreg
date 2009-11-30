#!/usr/bin/env python
#-*-mode: python -*- -*- coding: utf-8 -*-
"""

Command line interface to library.

"""
__version__="$Id$"

from optparse import OptionParser
import sys
import os

def scan_module_for_commands(module_name):
    
    result = {}
    module = sys.modules[module_name]
    for key in dir(module):
        if key.startswith("command_"):
            command = key[len("command_"):]
            command = command.replace("_", "-")
            result[command] = getattr(module, key)
    return result

class Command (object):
    pass

def command_register(options, source):
    import register

    register.register(source)

    # print >>sys.stderr, "Multiple deliverables selected, but that doesn't work with a single source-override."
    # sys.exit(1)
    
def command_make_command_links(options, dir=None):

    command_table = scan_module_for_commands(__name__)
    if dir is not None:
        os.chdir(dir)

    if os.path.exists("ldreg"):
        for key, value in command_table.items():
            new = "ldreg-"+key
            if os.path.exists(new):
                print new+": already exists"
            else:
                os.symlink("ldreg", new)
                print new+": link created"
    else:
        print "Please create/link 'ldreg' in that directory, first."

def run():
    global options

    command_table = scan_module_for_commands(__name__)

    given_command = None
    argv0 = os.path.basename(sys.argv[0])
    if argv0.startswith("ldreg-"):
        given_command = argv0[len("ldreg-"):]

    parser = OptionParser(usage="%prog [options] [command] [command_args]",
                          version=__version__)
    parser.set_defaults(verbose=True)
    parser.set_defaults(real=False)
    parser.set_defaults(inplace=False)
    parser.set_defaults(checker=None)
    parser.set_defaults(pdiff=True)
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", 
                      help="don't print status messages to stderr")
    parser.add_option("-D", "--debug",
                      action="append", dest="debugTags", 
                      help="turn on debugging of a particular type (try 'all')")
                      
    (options, args) = parser.parse_args()

    #if options.debugTags:
    #    debugtools.tags.update(options.debugTags)

    if not given_command:
        try:
            given_command = args[0]
        except IndexError:
            parser.print_help()
            print "Commands:"
            for name, func in sorted(command_table.items()):
                print "  %-30s"  % name,
                if func.__doc__:
                    print func.__doc__
                else:
                    print "No Documentation"
            sys.exit(1)
        args = args[1:]

    command = command_table[given_command]
    command(options, *args)

    #
    #    if len(args) < 0:

if __name__ == "__main__":
    import doctest, sys
    doctest.testmod(sys.modules[__name__])

    run()
