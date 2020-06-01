__author__ = 'are'
'''
Python Wrapper Class for Parsing / Writing pow files.

Class PowFile:

members:
str             filename:    The filename from which the data has been imported. -None- if not applicable.
[CTimeSeries]   timeSeries:  List of Time Series
'''

from ...obj.TimeSeries import CTimeSeries

class PowFile:

    filename = None
    timeSeries = [].copy()

    def __init__(self, filename=None):
        self.filename = filename
        if filename:
            self.loadFrom(filename)

    def loadFrom(self, filename):
        """Imports the data from a pow-file given by path <filename>"""
        self.filename = filename
        f = open(filename)
        self.timeSeries = [].copy()

        for l in f.readlines():
            if l[0] == "#":
                newTs = CTimeSeries()
                newTs.id = int(l.strip("#").strip())
                self.timeSeries.append(newTs)
            elif l[0] == "!":
                if self.timeSeries[-1].name == "":
                    self.timeSeries[-1].name = l.strip("!").strip()
            else:
                w = l.split()
                if len(w) == 2:
                    self.timeSeries[-1].DataPoints.append((w[0], w[1]))
        f.close()


    def saveTo(self, filename):
        """saves a pow file on the file system"""

        outfile = open(filename, "w")

        for ts in self.timeSeries:
            outfile.writelines("# " + str(ts.id)+"\n")
            outfile.writelines("! " + ts.name+"\n")
            outfile.writelines("! [type="+ts.type +
                               ";option="+ts.option +
                               ";timeunit="+ts.timeunit +
                               ";unitclass="+ts.unitclass +
                               ";userunit="+ts.userunit + "]\n")
            for dp in ts.DataPoints:
                if dp == "GAP":
                    outfile.writelines(" GAP\n")
                else:
                    outfile.writelines(" "+str(dp[0])+"\t"+str(dp[1])+"\n")
            outfile.writelines("END"+"\n")
        outfile.writelines("END")

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

    def removeDuplicateTS(self):
        self.timeSeries = list(set(self.timeSeries))