from ifm import Enum


class Ts:
    """
    Extension sub-class for IFM contributor's Extensions.
    Use this class to add functionality relating to MODEL TIME SERIES (formerly Power Functions).
    (Note: methods relating to Output Time Series - Histories - should be added to the .hist class)
    """

    def __init__(self, doc):
        self.doc = doc

    # add custom methods here