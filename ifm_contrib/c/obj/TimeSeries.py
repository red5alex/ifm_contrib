__author__ = 'are'
from datetime import datetime

class CTimeSeries:
    """
    Python Wrapper Class for time series.

    Class CTimeSeries:

    members:
    str             name        Name of the time seres
    int             id          Time Series ID
    [(float,float)] DataPoints  List of Data Points (
    str             type        Interpolation option:
                                    "Polylined"
                                    "Constant"
    str             option      Time options:
                                    "linear"
                                    "cyclic"
    str             timeunit    unit of time axis
    str             unitclass   unit class of values
    str             userunit    unit of values

    methods:
    __init__(filename)  Constructor. will call LoadFrom(filename) if filename is given, empty otherwise
    ___eq()___          euality operator
    ___hash()___        hash operator
    loadFrom(filename)  Clear all data and load new data from file (filename)
    saveTo(filename)    Write Data to File

    getTimes(self)                  returns a list with the time stamps
    getValueByTime(self, time)      returns the value at the given time
    getTotalTimeCoverageAndAverageValue(self):
    getAverageValue(self)           returns time averaged value (considers polylined and constant type series only
    getTotalTimeCoverage(self):     returns total time before initial and final point, excluding GAPs
    appendTimePoint(self, time, value): add an additional data point
    appendDatePoint(self, date, value, ref_date): add an additinal point by date
    insertGap(self, position=None): inserts a gap
    clean(self, pattern="equalMidPoints"): removes unncessery points from the time series

    see inline comments for more
    """


    name = ""
    id = -1
    DataPoints = []  # list of (float:time, float:value) tuples or "GAP"
    type = "Polylined"  # Polylined, Constant, ..
    option = "linear"
    timeunit = "d"
    unitclass = "CARDINAL"
    userunit = ""

    def __init__(self):
        self.name = ""
        self.id = -1
        self.DataPoints = []

    def getTimes(self):
        """:returns a list with the time stamps"""
        times = []
        for dp in self.DataPoints:
            times.append(dp[0])
        return times

    def getValueByTime(self, time):
        """:returns the value at the given time"""
        for dp in self.DataPoints:
            if dp[0] == time:
                return dp[1]

    def getTotalTimeCoverageAndAverageValue(self):
        """
        returns the average value of the time series.
        if time series has only one datapoint, its value is returned
        of no datapoint is available, None is returned
        """
        totaltimecoverage = 0.
        totalintegralvalue = 0.
        priorPoint = None

        # no data point:
        if len(self.DataPoints) == 0:
            return 0, None

        # one data point:
        if len(self.DataPoints) == 1:
            return 0, self.DataPoints[0][1]

        # multiple data points
        for p in self.DataPoints:
            if priorPoint is None or priorPoint == 'GAP':
                priorPoint = p
                continue
            elif p != 'GAP':
                t0, f0 = priorPoint
                t1, f1 = p

                t0=float(t0)
                t1=float(t1)
                f0=float(f0)
                f1=float(f1)

                totaltimecoverage += t1 - t0
                if self.type == "Polylined":
                    totalintegralvalue += (f0 + f1)/2 * (t1 - t0)
                if self.type == "Constant":
                    totalintegralvalue += f0 * (t1 - t0)
            priorPoint = p
        average_value = totalintegralvalue / totaltimecoverage
        return totaltimecoverage, average_value

    def getAverageValue(self):
        """
        The average value of the time series (based on temporal Integration. (Note that this is different
        from the standard deviation of a sample set.
        :return:the average value as <float>
        """
        t, f = self.getTotalTimeCoverageAndAverageValue()
        return f

    def getTotalTimeCoverage(self):
        t, f = self.getTotalTimeCoverageAndAverageValue()
        return t

    def getTimeValues(self):
        a = [x[0] for x in self.DataPoints]
        while 'G' in a:
            a.remove('G')  # "G" is returned at a GAP
        return a

    def getDataValues(self):
        a = [x[1] for x in self.DataPoints]
        while 'A' in a:
            a.remove('A')  # "A" is returned at a GAP
        return a

    def getMean(self):
        import statistics as st
        st.mean()
        pass

    def getTrend(self, initialtime=None, finaltime=None):
        a = self.getTimeValues()
        if len(a) < 2:
            return None
        if initialtime is None:
            initialtime = a[0]
        if finaltime is None:
            finaltime = a[-1]
        midtime = (initialtime + finaltime) / 2
        average = self.getAverageValue()

        return midtime, average


    def appendTimePoint(self, time, value):
        t = float(time)
        f = float(value)
        self.DataPoints.append((t, f))

    def appendDatePoint(self, date, value, ref_date):
        delta = date - ref_date
        days = delta.days
        seconds = delta.seconds
        time = days + seconds/(24*60*60)
        self.appendTimePoint(time, float(value))

    def insertGap(self, position=None):
        if position is not None:
            self.DataPoints.insert(position, "GAP")
        else:
            self.DataPoints.append("GAP")

    def clean(self, pattern="equalMidPoints"):
        """
        pattern:
         "equalMidPoints" removes all points i where f(i-1) = f(i) = f(i+1)
        """
        if pattern == "equalMidPoints":
            dp = self.DataPoints
            pass
            for i in range(len(dp)-2, 1, -1):  # step backwards as elements become deleted
                if 0 < i < len(dp):  # necessary to check if elements become deleted
                    if dp[i-1][1] == dp[i][1] == dp[i+1][1]:
                        del dp[i]
            pass


    def resample(self, rule, origin=datetime(1899,12,30)):
            """
            resample the data points.

            Parameters
            ----------

            rule : str
                    The resampling rule, e.g. "D" (daily), "W" (weekly), "6M" (every six month), "A" (annual.).
                    See https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases for a full list.

            """
            import pandas as pd

            # convert data points to df
            times = list(map(float, self.getTimes()))
            values = list(map(float, self.getDataValues()))
            df = pd.DataFrame(times, columns=["times"])
            df["value"] = values
            df["datetime"] = pd.to_datetime(df.times, unit="D", origin=origin)
            df.set_index("datetime", inplace=True)

            # resample
            df_resampled = df.resample(resample_rule).mean().dropna()
            df_resampled.reset_index(inplace=True)
            df_resampled["times_reverse"] =  (df_resampled.datetime - origin).dt.days

            # write back to data points
            self.DataPoints = [(t, v) for t,v in df_resampled[['times_reverse', 'value']].values]

    def __eq__(self, other):
        if self.DataPoints == other.DataPoints:
            return True
        else:
            return False

    def __hash__(self):
        hashstring = ""
        for dp in self.DataPoints:
            hashstring += str(dp[0]) + "," + str(dp[1])+"|"
        return hash(hashstring)
