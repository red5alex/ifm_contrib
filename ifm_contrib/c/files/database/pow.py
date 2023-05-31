__author__ = 'are'
from datetime import datetime
from ...obj.TimeSeries import CTimeSeries

class PowFile:
    
    def __init__(self, filename=None):
        """ 
        Class representing a pow file.

        Parameters
        ----------
        filename : str, optional
            path to pow file to be loaded. If omitted, class represents an empty pow-file with no time series.
        """
        self.timeSeries = []
        self.filename = filename
        if filename:
            self.load_from(filename)

    # depreciated
    def loadFrom(self, filename):
        import warnings
        warnings.warn("This function is depreciated. Use load_from() instead.", FutureWarning)
        self.load_from(filename)

    def load_from(self, filename):
        """
        Imports the data from a pow-file given by path `filename`.
        
        Parameters
        ----------
        filename : str
            path to pow file to be loaded
        """
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

    # depreciated
    def saveTo(self, filename):
        import warnings
        warnings.warn("This function is depreciated. Use save_to() instead.", FutureWarning)
        self.load_from(filename)

    def save_to(self, filename, progress_indicator=None):
        """
        Saves a pow file on the file system
        
        Parameters
        ----------

        filename : str
            filepath to save the pow-file.
        
        """
        outfile = open(filename, "w")

        if progress_indicator is not None:
            progress_indicator.bar_style=''
            progress_indicator.value = 0
            progress_indicator.min = 0
            progress_indicator.max = len(self.timeSeries)
            progress_indicator.description = "saving..."

        for ts in self.timeSeries:
            if progress_indicator is not None:
                progress_indicator.value += 1

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
        
        if progress_indicator is not None:
            progress_indicator.description="finished"
            progress_indicator.bar_style='success'
        

    def getTsNames(self):
        #:returns a list of strings containing the Names of the time series of the file"""
        names = []
        for ts in self.timeSeries:
            names.append(ts.name)
        return names

    def getTsByName(self, name):
        #returns the first time series with the name given by <name>. Returns None if not found.
        for ts in self.timeSeries:
            if ts.name == name:
                return ts
        return None

    def getTsById(self, id):
        #returns the first time series with the name given by <name>. Returns None if not found.
        for ts in self.timeSeries:
            if ts.id == id:
                return ts
        return None

    def removeDuplicateTS(self):
        self.timeSeries = list(set(self.timeSeries))
        