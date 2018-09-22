from ifm import Enum


class Sel:
    """
    Extension child-class for IFM contributor's Extensions.
    Use this class to add functionality relating to the PROBLEM SETTINGS of a FEFLOW model.
    """

    def __init__(self, doc):
        self.doc = doc

    # add custom methods here