from ifm import Enum

from .mesh_geopandas import MeshGpd

class Mesh:
    """
    Extension child-class for IFM contributor's Extensions.
    Use this class to add functionality relating to MESH (Nodes, Elements).
    """

    def __init__(self, doc):
        self.doc = doc

        # add custom child-classes here
        self.gdf = MeshGpd(doc)

    # add custom methods here

    def getCentroid(self, item, localcos=False, itemtype=Enum.SEL_ELEMENTAL):
        """
        Return the centroid of an element as (X, Y, Z) coordinate Tuple
        :param item: element number
        :param localcos: if True, Return local coordinate system (default: global)
        :param itemtype: {ifm.Enum.SEL_*} default ifm.Enum.SEL_ELEMENTAL
        :return:
        """
        if itemtype != ifm.Enum.SEL_ELEMENTAL:
            raise NotImplementedError("function not implemented for itemtype " + str(ifm.Enum.SEL_ELEMENTAL))

        dim = self.getNumberOfDimensions()
        NN = self.doc.getNumberOfNodesPerElement()

        x, y, z = (0., 0., 0.)
        for N in range(NN):
            n = self.doc.getNode(item, N)
            x += self.doc.getX(n)
            y += self.doc.getY(n)
            if dim == 3:
                z += self.doc.getZ(n)

        x = x / NN
        y = y / NN
        if dim == 3:
            z = z / NN
        else:
            z = None

        if not localcos:
            x += self.doc.getOriginX()
            y += self.doc.getOriginY()

        return x, y, z
