from ifm import Enum
from .content_pandas import ContentPd


class Content:
    """
    Functions regarding accessing information from the Content Panel
    """

    def __init__(self, doc):
        self.doc = doc

        # add custom child-classes here
        self.df = ContentPd(doc)

    # add custom methods here

