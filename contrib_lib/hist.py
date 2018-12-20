from ifm import Enum
from .hist_pandas import HistPd


class Hist:
    """
    Extension child-class for IFM contributor's Extensions.
    Use this class to add functionality relating to OBSERVATION HISTORIES.
    """

    def __init__(self, doc):
        self.doc = doc

        # add custom child-classes here
        self.df = HistPd(doc)

    # add custom methods here
