from ifm import Enum

from .mesh_geopandas import MeshGpd
from .mesh_pandas import MeshPd


class Mesh:
    """
    Functions to obtain data of FEFLOWs Data Panel.
    """

    def __init__(self, doc):
        self.doc = doc

        # add custom child-classes here
        self.df = MeshPd(doc)
        self.gdf = MeshGpd(doc)

    # add custom methods here

    def available_aux(self, silent=True, show_unavailable=False):
        """
        returns a dictionary with available auxiliary data items (separate for nodal and elemental items).
        :param silent: do not print to screen
        :param show_unavailable: also show unavailable items
        :return:
        """

        # define lists of all known aux items
        aux_E_strings = ['auxAquiferThickness',
                         'auxAspectRatio',
                         'auxAspectRatioBeta',
                         'auxAspectRatioGamma',
                         'auxCFLCondition',
                         'auxConditionNumber',
                         'auxCourantNumber',
                         'auxDelaunayViolatingTriangles',
                         'auxElementalVolumes',
                         'auxElementDiameter',
                         'auxLayerThickness',
                         'auxMaxDihedralAngles',
                         'auxMinDihedralAngles',
                         'auxPecletNumber',
                         'auxPseudoSat',
                         'auxQuadrangleMaxAngles',
                         'auxRelPerm',
                         'auxSquishIndex',
                         'auxTriangleMaxAngles']

        aux_N_strings = ['auxSliceDistance',
                         'auxNodalDepth']

        # check for existence - elemental
        elemental_avail = []
        elemental_unavail = []
        for auxid in aux_E_strings:
            param = self.doc.getParameter(Enum.P_AUXDIST_E, auxid)
            if param != None:
                elemental_avail.append(auxid)
            else:
                elemental_unavail.append(auxid)

        # check for existence - elemental
        nodal_avail = []
        nodal_unavail = []
        for auxid in aux_N_strings:
            param = self.doc.getParameter(Enum.P_AUXDIST_N, auxid)
            if param != None:
                nodal_avail.append(auxid)
            else:
                nodal_unavail.append(auxid)

        # print to screen
        if not silent:
            print("available elemental:\n\t", end="")
            print(",\n\t".join(elemental_avail))
            print()
            if show_unavailable:
                print("unavailable elemental:\n\t", end="")
                print(",\n\t".join(elemental_unavail))
                print()

            print("available nodal:\n\t", end="")
            print(",\n\t".join(nodal_avail))
            if show_unavailable:
                print("unavailable nodal:\n\t", end="")
                print(",\n\t".join(nodal_unavail))
                print()

        return {"nodal" : nodal_avail,
                "elemental" : elemental_avail}

    def get_imatrix(self, layer=None, split_quads_to_triangles=False, ignore_inactive=False, return_elements=False):
        """
        return the incidence matrix as [[int]].

        :param layer: specifies a layer number to return. If None (default), return all layers
        :param split_quads_to_triangles: split 4/8-nodes elements into two 3/6-noded elements
        :param ignore_inactive: do not include inactive elements
        :return: list (len=n_elements) of lists of node numbers
        """

        if layer is not None and (layer > self.doc.getNumberOfLayers() or layer <= 0):
            raise ValueError("layer number out of range.")

        ee = self.doc.getNumberOfElementsPerLayer()
        eee = self.doc.getNumberOfElements()

        if layer is None:
            element_range = range(self.doc.getNumberOfElements())
        else:
            if self.doc.getNumberOfDimensions() == 2:
                element_range = range(eee)
            elif self.doc.getNumberOfDimensions() == 3:
                element_range = range((layer - 1) * ee, layer * ee)
            else:
                raise NotImplementedError(str(self.doc.getNumberOfDimensions()) + " dimensions not supported")

        imat = []
        inactive = set()
        for e in element_range:
            if ignore_inactive and not self.doc.getMatElementActive(e):
                inactive.add(e)
                continue
            NN = self.doc.getNumberOfElementNodes(e)
            el_nodes = [self.doc.getNode(e, N) for N in range(NN)]
            if split_quads_to_triangles:
                if NN == 3 or NN == 6:
                    imat.append(el_nodes)
                elif NN == 4:
                    imat.append([el_nodes[1], el_nodes[2], el_nodes[3]])  # split quadrangle in 2 triangles
                    imat.append([el_nodes[3], el_nodes[0], el_nodes[1]])
                elif NN == 8:
                    imat.append([el_nodes[1], el_nodes[2], el_nodes[3], el_nodes[5], el_nodes[6],
                                 el_nodes[7]])  # split quadrangle in 2 triangles
                    imat.append([el_nodes[3], el_nodes[0], el_nodes[1], el_nodes[7], el_nodes[4], el_nodes[5]])

                    # imat.append(el_nodes[:3] + el_nodes[4:7])  # split 8-noded prism into 2 6-noded prisms
                    # imat.append(el_nodes[1:4] + el_nodes[4:])
                else:
                    raise NotImplementedError(str(NN) + "-noded element not supported")
            else:
                imat.append(el_nodes)

        if return_elements:
            return imat, list(set(element_range) - inactive)
        else:
            return imat

    def get_imatrix2d(self, slice=1, split_quads_to_triangles=False, ignore_inactive=False, return_elements=False):
        """
        return the incidence matrix as [[int]] of a slice.

        :param split_quads_to_triangles: split 4/8-nodes elements into two 3/6-noded elements
        :param ignore_inactive: do not include inactive elements
        :return: list (len=n_elements) of lists of node numbers
        """
        layer = slice
        if slice == self.doc.getNumberOfSlices():
            layer -= 1
        if slice > self.doc.getNumberOfSlices() or slice <= 0:
            raise ValueError("slice number out of range.")

        ee = self.doc.getNumberOfElementsPerLayer()
        eee = self.doc.getNumberOfElements()

        if self.doc.getNumberOfDimensions() == 2:
            element_range = range(eee)
        elif self.doc.getNumberOfDimensions() == 3:
            element_range = range((layer - 1) * ee, layer * ee)
        else:
            raise NotImplementedError(str(self.doc.getNumberOfDimensions()) + " dimensions not supported")

        imat = []
        inactive = set()
        for e in element_range:
            if ignore_inactive and not self.doc.getMatElementActive(e):
                inactive.add(e)
                continue

            NN = self.doc.getNumberOfElementNodes(e)
            el_nodes = [self.doc.getNode(e, N) for N in range(NN)]
            if split_quads_to_triangles:
                if NN == 3:
                    imat.append(el_nodes)
                elif NN == 6:
                    imat.append(el_nodes[:3])  # top nodes only
                elif NN == 4 or NN == 8:
                    imat.append([el_nodes[1], el_nodes[2], el_nodes[3]])  # split quadrangle in 2 triangles
                    imat.append([el_nodes[3], el_nodes[0], el_nodes[1]])
                else:
                    raise NotImplementedError(str(NN) + "-noded element not supported")
            else:
                imat.append(el_nodes)

        if return_elements:
            return (imat, list(set(element_range) - inactive))
        else:
            return imat

    def imatrix_as_array(self, global_cos=True, split_quads_to_triangles=False, layer=None, ignore_inactive=False,
                         use_cache=True, as_2d=False):
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
        elif layer is not None or as_2d:
            nn = self.doc.getNumberOfNodesPerSlice()
            ee = self.doc.getNumberOfElementsPerLayer()
            stop = 2
        else:
            nn = self.doc.getNumberOfNodes()
            ee = self.doc.getNumberOfElements()
            stop = 1

        x = np.array(self.doc.getParamValues(Enum.P_MSH_X)[:nn]) + X0
        y = np.array(self.doc.getParamValues(Enum.P_MSH_Y)[:nn]) + Y0

        # x = np.array([self.doc.getX(n) + X0 for n in range(nn)])
        # y = np.array([self.doc.getY(n) + Y0 for n in range(nn)])

        imat = []

        for e in range(ee):  # PerLayer

            if ignore_inactive and not self.doc.getMatElementActive(e):
                continue

            NN = int(self.doc.getNumberOfElementNodes(e) / stop)
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

        return imat

    def getCentroid(self, item, localcos=False, itemtype=Enum.SEL_ELEMENTAL):
        """
        Return the centroid of an element as (X, Y, Z) coordinate Tuple

        :param item: item number (e.g. element number)
        :type item: int
        :param localcos: Return local coordinate system if true, global otherwise (default).
        :type localcos: bool
        :param itemtype: item type (E
        :type itemtype: int (ifm.Enum.SEL_*)
        :return: coordinate (x,y,z) of the centroid
        :rtype: tuple
        """
        if itemtype != Enum.SEL_ELEMENTAL:
            raise NotImplementedError("function not implemented for itemtype " + str(Enum.SEL_ELEMENTAL))

        dim = self.doc.getNumberOfDimensions()
        NN = self.doc.getNumberOfElementNodes(item)

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

    def get_borders(self):
        """
        Return border nodes as a dictionary {key: border number, value: list of node numbers}.

        :return:
        """
        borders = {}
        for border in range(self.doc.getNumberOfBorders()):
            borders[border] = [self.doc.getBorderNode(border, n) for n in
                               range(self.doc.getNumberOfBorderNodes(border))]
        return borders

    def mlw(self, global_cos=True):
        """
        Return a dictionary with information on all Multi-Layer wells in the model.

        :return: dictionary
        :rtype: dict
        """

        if global_cos:
            X0, Y0 = self.doc.getOriginX(), self.doc.getOriginY()
        else:
            X0, Y0 = 0, 0

        l_mlw = range(self.doc.getNumberOfMultiLayerWells())
        data = {
            "name": [self.doc.queryMultiLayerWellInfo(self.doc.getMultiLayerWellBottomNode(mlw)).getName() for mlw in l_mlw],
            "radius": [self.doc.queryMultiLayerWellInfo(self.doc.getMultiLayerWellBottomNode(mlw)).getRadius() for mlw in l_mlw],
            "mlw_id": [self.doc.queryMultiLayerWellInfo(self.doc.getMultiLayerWellBottomNode(mlw)).getId() for mlw in l_mlw],
            "rate_tsid": [self.doc.getMultiLayerWellAttrTSID(mlw, Enum.MLW_RATE) for mlw in l_mlw],
            "rate_value": [self.doc.getMultiLayerWellAttrValue(mlw, Enum.MLW_RATE) for mlw in l_mlw],
            "bcc_hmin_tsid": [self.doc.getMultiLayerWellAttrTSID(mlw, Enum.MLW_BCC_HMIN) for mlw in l_mlw],
            "bcc_hmin_value": [self.doc.getMultiLayerWellAttrValue(mlw, Enum.MLW_BCC_HMIN) for mlw in l_mlw],
            "bcc_hmax_tsid": [self.doc.getMultiLayerWellAttrTSID(mlw, Enum.MLW_BCC_HMAX) for mlw in l_mlw],
            "bcc_hmax_value": [self.doc.getMultiLayerWellAttrValue(mlw, Enum.MLW_BCC_HMAX) for mlw in l_mlw],
            "bottom_node": [self.doc.getMultiLayerWellBottomNode(mlw) for mlw in l_mlw],
            "top_node": [self.doc.getMultiLayerWellTopNode(mlw) for mlw in l_mlw],
            "top_x": [self.doc.getX(self.doc.getMultiLayerWellTopNode(mlw)) + X0 for mlw in l_mlw],
            "top_y": [self.doc.getY(self.doc.getMultiLayerWellTopNode(mlw)) + Y0 for mlw in l_mlw],
            "top_z": [self.doc.getZ(self.doc.getMultiLayerWellTopNode(mlw)) for mlw in l_mlw],
            "bottom_x": [self.doc.getX(self.doc.getMultiLayerWellBottomNode(mlw)) + X0 for mlw in l_mlw],
            "bottom_y": [self.doc.getY(self.doc.getMultiLayerWellBottomNode(mlw)) + Y0 for mlw in l_mlw],
            "bottom_z": [self.doc.getZ(self.doc.getMultiLayerWellBottomNode(mlw)) for mlw in l_mlw],
        }
        return data
