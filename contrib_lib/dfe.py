from ifm import Enum
from .dfe_pandas import DfePd


class Dfe:
    """
    Functions regarding Discrete Feature Elements.
    """

    def __init__(self, doc):
        self.doc = doc

        # add custom child-classes here
        self.df = DfePd(doc)


    # add custom methods here

    def setFracArea(self, fracid, value):
        """
        Set a new cross-section area for the given DFE
        :param fracid: index of the DFE
        :param value: new area value
        :return: None
        """
        self.doc.setFracArea(fracid, value,
                             Enum.ALL_FRAC_TYPES, Enum.ALL_FRAC_MODES, Enum.ALL_FRAC_LAWS)

    def setFracFlowConductivity(self, fracid, value):
        """
        Set a new hydraulic conductivity for the given DFE
        :param fracid: index of the DFE
        :param value: new area value
        :return: None
        """
        self.doc.setFracFlowConductivity(fracid, value,
                             Enum.ALL_FRAC_TYPES, Enum.ALL_FRAC_MODES, Enum.ALL_FRAC_LAWS)
