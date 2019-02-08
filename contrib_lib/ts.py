# from ifm import Enum
from .ts_pandas import TsPd


class Ts:
    """
    Extension sub-class for IFM contributor's Extensions.
    Use this class to add functionality relating to MODEL TIME SERIES (formerly Power Functions).
    (Note: methods relating to Output Time Series - Histories - should be added to the .hist class)
    """

    def __init__(self, doc):
        self.doc = doc

        # add custom child-classes here
        self.df = TsPd(doc)

    # add custom methods here
    def info(self):
        """
        Returns information on existing time series (formerly power functions) as a list of tuples:
        [(Time Series ID, Comment, Number of Points, cyclic, interpolation kind)]
        """
        info = []
        tsid = 0
        while True:
            tsid = self.doc.powerGetCurve(tsid)
            if tsid == -1:
                break
            info.append((tsid,
                         self.doc.powerGetComment(tsid),
                         self.doc.powerGetNumberOfPoints(1),
                         self.doc.powerIsCyclic(1),
                         self.doc.powerGetInterpolationKind(1)))
        return info

    def points(self, tsid):
        """
        Returns the values of a given time series as a list of (time, value) tuples.

        :param tsid:             time series ID
        :type tsid:              int or convertible to int
        :return:                 list of tuples
        """

        # make sure tsid is a valid number
        try:
            tsid = int(tsid)
        except ValueError:
            raise ValueError("tsid must be of type int or convertible to type int")

        return [self.doc.powerGetPoint(tsid, i) for i in range(self.doc.powerGetNumberOfPoints(tsid))]

    def exists(self, tsid):
        """
        Test if time series (formerly power function) exists.

        :param tsid:  time series ID
        :type tsid:   int or convertible to int
        :return:
        """

        # make sure tsid is a valid number
        try:
            tsid = int(tsid)
        except ValueError:
            raise ValueError("tsid must be of type int or convertible to type int")

        # check if ts is in list of tsids
        tsid_existing = [i[0] for i in self.doc.c.ts.info()]
        if tsid in tsid_existing:
            return True
        else:
            return False
