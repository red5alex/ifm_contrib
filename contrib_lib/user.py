from ifm import Enum
from .user_pandas import UserPd

class User:
    """
    Functions regarding User Data (Distributions and Expressions)
    """

    def __init__(self, doc):
        self.doc = doc

        # add custom child-classes here
        self.df = UserPd(doc)

    def get_type(self, name):
        """
        Returns the item type ("ELEMENTAL" or "NODAL) and distribution type ("DISTRIBUTION" or "EXPRESSION") of a 
        given user distribution. Returns "NOT_FOUND for both values if distribution does not exist.

        :param name: Name of the distribution
        :type name: str
        :return: tuple ({"ELEMENTAL"|"NODAL"|"NOT_FOUND"}, {"DISTRIBUTION"|"EXPRESSION"|"NOT_FOUND"})
        :rtype: str
        """ 

        if self.doc.getElementalRefDistrIdByName(name) != -1:
            item_type = "ELEMENTAL"
            user_type = "DISTRIBUTION"
        elif self.doc.getNodalRefDistrIdByName(name)  != -1:
            item_type = "NODAL"
            user_type = "DISTRIBUTION"
        if self.doc.getElementalExprDistrIdByName(name) != -1:
            item_type = "ELEMENTAL"
            user_type = "EXPRESSION"
        elif self.doc.getNodalExprDistrIdByName(name)  != -1:
            item_type = "NODAL"
            user_type = "EXPRESSION"
        else:
            item_type = "NOT_FOUND"
            user_type = "NOT_FOUND"
            
        return item_type, user_type

    def exists(self, name):
        """
        Test if a user distribution/expression exists.
        
        :param name: Name of the distribution
        :type name: str
        :return: True if exists, False otherwise
        """
        item_type, _ = self.doc.c.user.get_type(name)
        if item_type == "NOT_FOUND":
            return False
        else:
            return True

    def create(self, seltype, distname, itemlist=None, overwrite_existing=False):
        """
        Create a new user distribution of given type and name.
        Populate the distribution with item values if provided.

        :param disttype:  {ifm.Enum.SEL_NODAL|ifm.Enum.SEL_ELEMENTAL}
        :type disttype:   ifm.Enum
        :param distname:  Name of selection
        :type distname:   str
        :param values: list of item indices (optional)
        :type values:  [float]
        :param overwrite_existing: If True, overwrite an existing distribution (will raise ValueError otherwise)
        :type overwrite_existing: bool
        :return:         the id of the distribution
        """

        try:
            if itemlist is not None:
                itemlist = list(itemlist)
        except TypeError:
            raise TypeError("itemlist must be list or list-like!")

        if self.doc.c.user.exists(distname):
            if overwrite_existing:
                if seltype == Enum.SEL_NODAL:
                    ref_id = self.doc.getNodalRefDistrIdByName(distname)
                    if ref_id == -1:
                        raise RuntimeError("Cannot overwrite, an elemental user distribution {} does already exist.".format(distname))
                elif seltype == Enum.SEL_ELEMENTAL:
                    ref_id = self.doc.getNodalRefDistrIdByName(distname)
                    if ref_id == -1:
                        raise RuntimeError("Cannot overwrite, an nodal user distribution {} does already exist.".format(distname))
                else:
                    raise ValueError("Unknwon seltype {}!".format(seltype))
            else:
                raise RuntimeError("user distribution {} does already exists (set overwrite_existing=True to update).".format(distname))
        else:  # selection does not exist
            if seltype == Enum.SEL_NODAL:
                ref_id = self.doc.createNodalRefDistr(distname)
            else:
                ref_id = self.doc.createElementalRefDistr(distname)

        if seltype == Enum.SEL_NODAL:
            self.doc.createNodalRefDistr(distname)
            if itemlist is not None:
                if len(itemlist)!=self.doc.getNumberOfNodes():
                    raise RuntimeError("len(itemlist) must match number of nodes!")
                self.doc.setNodalRefDistrValues(ref_id, itemlist)
        else:
            if itemlist is not None:
                if len(itemlist)!=self.doc.getNumberOfElements():
                    raise RuntimeError("len(itemlist) must match number of nodes!")
                self.doc.setElementalRefDistrValues(ref_id, itemlist)

        return ref_id