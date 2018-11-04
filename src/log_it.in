#!/usr/bin/env python3

import os.path
import time


def log_it(thing, newfile=False):

    """Provide a quick and dirty logging facility

    Args:
        thing   : the string to be written to the log file
        newfile :  boolean - if True the log file is created, if False it is appended to
    """

    filename = os.path.expanduser("~/tmp/log")
    if os.path.isdir(os.path.expanduser("~/tmp")):
        if newfile:
            thefile = open(filename, 'w')
        else:
            thefile = open(filename, 'a')

        thefile.write(time.strftime("%d %b %X: " + thing + "\n"))
        thefile.close()
