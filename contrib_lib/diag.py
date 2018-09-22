from ifm import Enum


class Diag:
    """
    Extension child-class for IFM contributor's Extensions.
    Use this class to add functionality relating to diagnostic tests on the model.
    """

    def __init__(self, doc):
        self.doc = doc

    # add custom methods here