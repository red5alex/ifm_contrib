from ifm import Enum


class Sel:
    """
    Extension child-class for IFM contributor's Extensions.
    Use this class to add functionality relating to the PROBLEM SETTINGS of a FEFLOW model.
    """

    def __init__(self, doc):
        self.doc = doc

    # add custom methods here
    def list(self, selname, seltype=None):
        # try all supported types
        if seltype is None:
            seltypes = [Enum.SEL_NODES,
                        Enum.SEL_ELEMS,
                        Enum.SEL_EDGES,
                        Enum.SEL_FRACS]
        else:
            seltypes = [seltype]

        for stype in seltypes:
            selid = self.doc.findSelection(stype, selname)
            if selid != -1:  # if selection is found
                return self.doc.getSelectionItems(stype, selid)

        # if selection is not found
        return []

    def set(self, selname, seltype=None):
        return set(self.list(selname, seltype=seltype))

    def getSelectionNames(self, seltype=None):
        if seltype is None:
            seltypes = [Enum.SEL_NODES,
                        Enum.SEL_ELEMS,
                        Enum.SEL_EDGES,
                        Enum.SEL_FRACS]
            selection_names = []
            for seltype in seltypes:
                nsel = self.doc.getNumberOfSelections(seltype)
                selection_names += [self.doc.getSelectionName(seltype, selid) for selid in range(nsel)]
            return selection_names

        else:
            nsel = self.doc.getNumberOfSelections(seltype)
            return [self.doc.getSelectionName(seltype, selid) for selid in range(nsel)]
