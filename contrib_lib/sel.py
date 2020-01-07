from ifm import Enum


class Sel:
    """
    Functions for working with selections.
    """

    def __init__(self, doc):
        self.doc = doc

    # add custom methods here

    def list(self, selname, seltype=None):
        """
        Return the item indices of the given selection as a list.

        :param selname: name of the selection
        :type selname:  str
        :param seltype: type of the selection (optional)
        :type seltype:  ifm.Enum or None
        :return:        list of item indices
        """

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
        """
        Return the item indices of the given selection as a set.

        :param selname: name of the selection
        :type selname:  str
        :param seltype: type of the selection
        :type seltype:  ifm.Enum or None
        :return:        set of item indices
        """
        return set(self.list(selname, seltype=seltype))

    def getSelectionNames(self, seltype=None):
        """
        Return a list of names of selections in the model

        :param seltype: Selection type (return all if None).
        :type seltype:  ifm.Enum or None.
        :return:
        """
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
        Returns the type of a given selection. Returns -1 (=Enum.SEL_INVALID) if selection does not exist.

        :param selection: name of the selection
        :type selection: str
        :return: type of selection
        :rtype: ifm.Enum
        """
        for seltype in [Enum.SEL_NODAL,
                        Enum.SEL_ELEMENTAL,
                        Enum.SEL_EDGES,
                        # Enum.SEL_FACES,  ARE: inactive, probably FEFLOW bug
                        Enum.SEL_FRACS]:

            selections = self.doc.c.sel.getSelectionNames(seltype)
            if selection in selections:
                return seltype
        return Enum.SEL_INVALID

    def create(self, seltype, selname, itemlist=None, overwrite_existing=False):
        """
        create a new selection of given type and name. Populate the selection if itemlist if provided.

        :param seltype:  Type of selection type
        :type seltype:   ifm.Enum
        :param selname:  Name of selection
        :type selname:   str
        :param itemlist: list of item indices (optional)
        :type itemlist:  [int]
        :return:         the id of the selection
        """

        # raise error if selection already exists
        if not self.doc.findSelection(seltype, selname) != -1:
            selid = self.doc.createSelection(seltype, selname)
        else:
            if overwrite_existing:
                selid = self.doc.findSelection(seltype, selname)
                self.doc.c.sel.clear(selname)
            else:
                raise ValueError("Selection {} does already exist!".format(selname))

        # populate if itemlist is provided
        if itemlist is not None:
            for i in itemlist:
                self.doc.setSelectionItem(seltype, selid, i)

        return selid

    def convert(self, selection, to_type):
        """
        Converts a selection to a selection of the given type.
        Currently only support elemental to nodal.

        :param selection: Name of the selection to be converted
        :type selection:  str
        :param to_type:   type of the selection to return
        :type to_type:    ifm.Enum
        :return:          list of converted items
        """
        from_type = self.doc.c.sel.getSelectionType(selection)

        if from_type == Enum.SEL_INVALID:
            raise ValueError("Selection {} not found".format(selection))

        if to_type == Enum.SEL_INVALID:
            raise ValueError("Cannot convert to Invalid Type!")

        # no conversion if types are equal
        if from_type == to_type:
            return self.doc.c.sel.list(selection)

        # elemental to nodal
        if from_type == Enum.SEL_ELEMENTAL and to_type == Enum.SEL_NODAL:
            i_matrix = self.doc.c.mesh.get_imatrix()
            to_sel = set()
            for e in self.doc.c.sel.list(selection):
                to_sel = to_sel.union(set(i_matrix[e]))

            return sorted(list(to_sel))

        # nodal to elemental
        if from_type == Enum.SEL_NODAL and to_type == Enum.SEL_ELEMENTAL:

            to_sel = set()
            for n in self.doc.c.sel.list(selection):
                for E in range(self.doc.getNumberOfNodeElements(n)):
                    to_sel.add(self.doc.getElement(n, E))

            return sorted(list(to_sel))

        # all other cases not implemented
        raise NotImplementedError()

    def clear(self, selname, seltype=None):
        """
        :param selname: name of the selection to be updates
        :type selname: str
        :param seltype: list of allowed types of the selections (optional, default None - type will be determined)
        :type seltype: list
        :return: bool
        """
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
                while self.doc.getSelectionItemCount(stype, selid) > 0:
                    first_item = self.doc.pdoc.getSelectionItems(stype, selid)[0]
                    self.doc.clearSelectionItem(stype, selid, first_item)
                return True

        # if getting here, selection was not found
        raise StandardError("selection '{}' not found in model".format(selname))

    def update(self, selname, itemlist, seltype=None):
        """
        Updates a selection to match the current item list
        :param selname: name of the selection to be updates
        :type selname: str
        :param itemlist: list with item numbers
        :type itemlist: list
        :param seltype: list of allowed types of the selections (optional, default None - type will be determined)
        :type seltype: list
        :return: bool
        """
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
                # clear and repopulate all items.
                self.doc.c.sel.clear(selname)
                [self.doc.setSelectionItem(stype, selid, i) for i in itemlist]
                return True

        # if getting here, selection was not found
        raise StandardError("selection '{}' not found in model".format(selname))
