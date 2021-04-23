from ifm import Enum

from .sel_pandas import SelPd


class Sel:
    """
    Functions for working with selections.
    """

    def __init__(self, doc):
        self.doc = doc

        # add custom child-classes here
        self.df = SelPd(doc)

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
        raise ValueError("Selection {} not found".format(selname))

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
        Legacy, use selections() instead
        """
        return self.doc.c.sel.selections(seltype=seltype)

    def selections(self, seltype=None):
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

            selections = self.doc.c.sel.selections(seltype)
            if selection in selections:
                return seltype
        return Enum.SEL_INVALID

    def create(self, seltype, selname, itemlist=None, overwrite_existing=False):
        """
        Create a new selection of given type and name. Populate the selection if itemlist if provided.

        :param seltype:  Type of selection type
        :type seltype:   ifm.Enum
        :param selname:  Name of selection
        :type selname:   str
        :param itemlist: list of item indices (optional)
        :type itemlist:  [int] or int
        :param overwrite_existing: If True, overwrite an existing selection. Raises ValueError if False (default).
        :type overwrite_existing: bool
        :return:         the id of the selection
        """

        # parameter handling
        if type(itemlist) not in [list, int]:
            raise ValueError("itemlist must be of type [int] or int")
        if type(itemlist)==int:
            itemlist = [itemlist]
        
        # create selection if it does not exist
        if self.doc.findSelection(seltype, selname) == -1:
            selid = self.doc.createSelection(seltype, selname)
        else:
            # clear existing selection if allowed
            if overwrite_existing:
                selid = self.doc.findSelection(seltype, selname)
                self.doc.c.sel.clear(selname)
            else:
                # raise Error otherwise
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
            to_sel = []
            for e in self.doc.c.sel.list(selection):
                for n in i_matrix[e]:
                    to_sel.append(n)
            return sorted(set(to_sel))  # only unique values

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
        raise ValueError("selection '{}' not found in model".format(selname))

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
        raise RuntimeError("selection '{}' not found in model".format(selname))

    def get_xybounds(self, selection, global_cos=True, zoom=1.):
        """
        Return the bounding box of the given selection as tuple (minx, maxx, miny, maxy).
        If elemental selection, bounding box is calculated from centroids.
        :param selection: the name of the selection.
        :param zoom: zoom factor to be applied.
        :return:
        """
        # get the min, max x/y of the selection
        if self.doc.c.sel.getSelectionType(selection) == Enum.SEL_NODAL:
            df = self.doc.c.mesh.df.nodes(selection=selection, global_cos=global_cos)
        elif self.doc.c.sel.getSelectionType(selection) == Enum.SEL_ELEMENTAL:
            df = self.doc.c.mesh.df.elements(selection=selection, global_cos=global_cos, centroids=True)
            df["X"] = df.centroid.apply(lambda x: x[0])
            df["Y"] = df.centroid.apply(lambda x: x[1])
        else:
            raise NotImplementedError("This type of selection is not implemented yet")
        minx, maxx = df.X.min(), df.X.max()
        miny, maxy = df.Y.min(), df.Y.max()

        # zoom in or out
        dx = maxx - minx
        dy = maxy - miny
        minx -= dx * (zoom - 1.)
        maxx += dx * (zoom - 1.)
        miny -= dy * (zoom - 1.)
        maxy += dy * (zoom - 1.)

        return minx, maxx, miny, maxy

    def delete(self, selname, seltype=None, ignore_if_missing=False):
        """
        Delete a selection of the given name. Return True if successful.
        
        :param selname: name of the selection to be updates
        :type selname: str
        :param seltype: list of allowed types of the selections (optional, default None - type will be determined)
        :type seltype: list
        :param ignore_if_missing: If False (default), raise ValueError if selection is not found.
        :type ignore_if_missing: bool 
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
                self.doc.deleteSelection(stype, selid)
                return True

        if ignore_if_missing:
            return False

        # if getting here, selection was not found
        raise ValueError("selection '{}' not found in model".format(selname))
