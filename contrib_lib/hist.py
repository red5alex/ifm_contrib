from ifm import Enum
from .hist_pandas import HistPd


class Hist:
    """
    Functions to obtain data of FEFLOWs chart panels
    """

    def __init__(self, doc):
        self.doc = doc

        # add custom child-classes here
        self.df = HistPd(doc)

    # add custom methods here
