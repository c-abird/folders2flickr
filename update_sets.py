#!/usr/bin/env python
"""
Command line folders2flickr interface
"""

try:
    import f2flickr.uploadr
    from f2flickr.tags2set import createSets
    from f2flickr.configuration import configdict

    historyFile = configdict.get('history_file')
    createSets(None, historyFile)

except IOError, ex:
    print ex
