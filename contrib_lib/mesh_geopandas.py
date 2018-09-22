from ifm import Enum


class MeshGpd:

    def __init__(self, doc):
        self.doc = doc


    def imatrix_as_array(self, global_cos=True):
        """
        load the nodes coordinates, the incidence matrix into a numpy matrix
        :param global_cos: If True, use global coordinate system (default: local)
        :return: tuple(numpy.Array) (x, y, imat)
        """

        import numpy as np

        dd = self.doc.getNumberOfDimensions()
        if global_cos:
            X0 = self.doc.getOriginX()
            Y0 = self.doc.getOriginY()
        else:
            X0 = Y0 = 0

        x = []
        y = []

        if dd == 2:
            nn = self.doc.getNumberOfNodes()
            ee = self.doc.getNumberOfElements()
            stop = 1
        else:
            nn = self.doc.getNumberOfNodesPerSlice()
            ee = self.doc.getNumberOfElementsPerLayer()
            stop = 2

        for n in range(nn):
            x.append(self.doc.getX(n) + X0)
            y.append(self.doc.getY(n) + Y0)

        x = np.array(x)
        y = np.array(y)

        imat = []

        for e in range(ee):  # PerLayer
            if not self.doc.getMatElementActive(e):
                continue
            NN = self.doc.getNumberOfElementNodes(e) / stop
            element_nodes = [self.doc.getNode(e, N) for N in range(NN)]
            if NN == 3:
                imat.append(element_nodes)
            elif NN == 4:
                imat.append(element_nodes[:3])  # split quadrangle in 2 triangles
                imat.append(element_nodes[1:])
            else:
                raise ValueError(str(NN * 2) + "-noded element not supported")

        return x, y, imat

    def getGeoDatframe(self, global_cos=True):
        """
        Get the mesh as a GeoPandas GeoDataFrame.
        :param global_cos: If True, use global coordinate system (default: local)
        :return: GeoDataFrame
        """

        import geopandas as gpd
        from shapely.geometry import Point, Polygon

        x, y, imat = self.imatrix_as_array(global_cos=global_cos)
        # create a GeoDataFrame from the mesh and save as shape file
        gdf_elements = gpd.GeoDataFrame([Polygon([(x[n], y[n]) for n in element]) for element in imat])
        gdf_elements.columns = ["element_shape"]
        gdf_elements.set_geometry("element_shape", inplace=True)
        gdf_elements.index.name = "ELEMENT"
        gdf_elements["ELEMENT"] = gdf_elements.index.values
        gdf_elements["AREA"] = gdf_elements.geometry.area

        return gdf_elements
