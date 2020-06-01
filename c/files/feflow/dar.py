__author__ = 'are'

__author__ = 'are'
'''
Python Wrapper Class for Parsing / Writing par files.

Class ParFile:

members:
str             filename:    The filename from which the data has been imported. -None- if not applicable.



'''

from trunk.feflowpy.abstract.CTimeSeries import CTimeSeries

class ParFile:

    filename = None
    timeSeries = [].copy()

    def __init__(self, filename=None):
        self.filename = filename
        if filename:
            self.loadFrom(filename)

    def loadFrom(self, filename):
        """Imports the data from a pow-file given by path <filename>"""

        def readLocationBlock():
            pass

        def readObsBlock():
            pass

        self.filename = filename
        f = open(filename)
        self.timeSeries = [].copy()

        for l in f.readlines():

            if "LOCATION (GLOBAL AND LOCAL)" in l:
                readObsBlock()
            elif l[0] == "!":
                if self.timeSeries[-1].name == "":
                    self.timeSeries[-1].name = l.strip("!").strip()
            else:
                w = l.split()
                if len(w) == 2:
                    self.timeSeries[-1].DataPoints.append((w[0], w[1]))
        f.close()

    def getTsNames(self):
        """:returns a list of strings containing the Names of the time series of the file"""
        names = []
        for ts in self.timeSeries:
            names.append(ts.name)
        return names

    def getTsByName(self, name):
        """:returns the first time series with the name given by <name>. Returns None if not found."""
        for ts in self.timeSeries:
            if ts.name == name:
                return ts
        return None

    def getTsById(self, id):
        """:returns the first time series with the name given by <name>. Returns None if not found."""
        for ts in self.id:
            if ts.id == id:
                return ts
        return None