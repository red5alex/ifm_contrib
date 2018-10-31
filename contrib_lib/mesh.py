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
        self.df = MeshGpd(doc)

    # add custom methods here

    def imatrix_as_array(self, global_cos=True, split_quads_to_triangles=False, layer=None, ignore_inactive=False):
        """
        load the nodes coordinates, the incidence matrix into a numpy matrix
        :param global_cos: If True, use global coordinate system (default: local)
        :return: tuple(numpy.Array) (x, y, imat)
        """

        import numpy as np

        if global_cos:
            X0 = self.doc.getOriginX()
            Y0 = self.doc.getOriginY()
        else:
            X0 = Y0 = 0

        if self.doc.getNumberOfDimensions() == 2:
            nn = self.doc.getNumberOfNodesPerSlice()
            ee = self.doc.getNumberOfElementsPerLayer()
            stop = 1
        elif layer is not None:
            nn = self.doc.getNumberOfNodesPerSlice()
            ee = self.doc.getNumberOfElementsPerLayer()
            stop = 2
        else:
            nn = self.doc.getNumberOfNodes()
            ee = self.doc.getNumberOfElements()
            stop = 1

        x = self.doc.getParamValues(Enum.P_MSH_X)[:nn]
        y = self.doc.getParamValues(Enum.P_MSH_Y)[:nn]

        # x = np.array([self.doc.getX(n) + X0 for n in range(nn)])
        # y = np.array([self.doc.getY(n) + Y0 for n in range(nn)])

        imat = []

        for e in range(ee):  # PerLayer

            if ignore_inactive and not self.doc.getMatElementActive(e):
                continue

            NN = self.doc.getNumberOfElementNodes(e) / stop
            element_nodes = [self.doc.getNode(e, N) for N in range(NN)]


            if split_quads_to_triangles:
                if NN == 3:
                    imat.append(element_nodes)
                elif NN == 4:
                    imat.append(element_nodes[:3])  # split quadrangle in 2 triangles
                    imat.append(element_nodes[1:])
                else:
                    raise ValueError(str(NN * 2) + "-noded element not supported")
            else:
                imat.append(element_nodes)

        return x, y, imat

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
