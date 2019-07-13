from ifm import Enum
from .content_pandas import ContentPd


class Content:
    """
    Extension child-class for IFM contributor's Extensions.
    Use this class to add functionality relating to CONTENT.
    """

    def __init__(self, doc):
        self.doc = doc

        # add custom child-classes here
        self.df = ContentPd(doc)

    # add custom methods here

