# from ifm import Enum
import pandas as pd


class TsPd:

    def __init__(self, doc):
        self.doc = doc

    def info(self):
        """
        Returns a pandas.DataFrame with information on existing user distributions.
        """
        [self.doc.getElementalRefDistrName(i) for i in self.doc.pdoc.getNumberOfElementalExprDistr()]
        [self.doc.getElementalExprDistrName(i) for i in self.doc.pdoc.getNumberOfElementalExprDistr()]
        [self.doc.getNodalRefDistrName(i) for i in self.doc.pdoc.getNumberOfNodalExprDistr()]
        [self.doc.getNodalExprDistrName(i) for i in self.doc.pdoc.getNumberOfNodalExprDistr()]
