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

    def getSelectionType(self, selection):
        """
        Returns the type of the selection. Returns -1 (Enum.SEL_INVALID) if selection does not exist.
        :param selection: name of the selection to be tested
        :return: type of selection
        """
        for seltype in [Enum.SEL_NODAL,
                        Enum.SEL_ELEMENTAL,
                        Enum.SEL_EDGES,
                        # Enum.SEL_FACES,  ARE: inactive, probably FEFLOW bug
                        Enum.SEL_FRACS]:

            selections = self.doc.c.sel.getSelectionNames(seltype)
            if selection in selections:
                return (seltype)
        return Enum.SEL_INVALID

    def convert(self, selection, to_type):
        """
        Converts a selection to a selection of the given type
        :param selection:
        :param to_type:
        :return:
        """
        from_type = self.doc.c.sel.getSelectionType(selection)

        if from_type==Enum.SEL_INVALID:
            raise ValueError("Selection {} not found".format(selection))

        if to_type==Enum.SEL_INVALID:
            raise ValueError("Cannot convert to Invalid Type!")

        # no conversion if types are equal
        if from_type==to_type:
            return self.doc.c.sel.list(selection)

        # elemental to nodal
        if from_type == Enum.SEL_ELEMENTAL and to_type == Enum.SEL_NODAL:
            i_matrix = self.doc.c.mesh.get_imatrix()
            to_sel = set()
            for e in self.doc.c.sel.list(selection):
                to_sel = to_sel.union(set(i_matrix[e]))

            return sorted(list(to_sel))

        # all other cases not implemented
        raise NotImplementedError()
