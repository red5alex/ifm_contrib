from ifm import Enum
from .dfe_pandas import DfePd


class Dfe:
    """
    Extension child-class for IFM contributor's Extensions.
    Use this class to add functionality relating to MESH (Nodes, Elements).
    """

    def __init__(self, doc):
        self.doc = doc

        # add custom child-classes here
        self.df = DfePd(doc)


    # add custom methods here