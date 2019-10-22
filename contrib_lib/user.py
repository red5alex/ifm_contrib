# from ifm import Enum
from .ts_pandas import TsPd

class User:
    """
    Extension sub-class for IFM contributor's Extensions.
    Use this class to add functionality relating to user distributions and expressions
    """

    def __init__(self, doc):
        self.doc = doc

        # add custom child-classes here
        self.df = TsPd(doc)
