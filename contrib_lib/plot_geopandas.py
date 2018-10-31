from ifm import Enum


class PlotGpd:

    def __init__(self, doc):
        self.doc = doc

    def _get_nodal_values(self, item):
        """
        get array of nodal values
        """
        import numpy as np

        # get range of nodes (2D, 3D)
        # TODO: Support for inactive elements
        if self.doc.getNumberOfDimensions() == 2:
            nodes = range(self.doc.getNumberOfNodes())
        else:
            nodes = range(self.doc.getNumberOfNodesPerSlice())

        # read values into array
        if item == "Head":
            values = [self.doc.getResultsFlowHeadValue(n) for n in nodes]
        else:
            raise NotImplementedError("value " + str(item) + " not implemented")
        # TODO: Implement item, subitem (e.g., Mass, species=1)
        values = np.array(values)

        # replace nan heads (inactive nodes) with mean value
        inds = np.where(np.isnan(values))
        h_mean = values[~np.isnan(values)].mean()
        for i in inds:
            values[i] = h_mean

        return values

    def fringes(self, item, subitem=0, global_cos=True):
        """
        Get Fringes Polygons.
        :param global_cos: If True, use global coordinate system (default: local)
        :return: GeoDataFrame
        """

        import geopandas as gpd
        from shapely.geometry import Polygon
        import numpy as np
        import matplotlib.pyplot as plt
        import matplotlib.tri as tri

        # read incidence matrix and node values
        x, y, imat = self.doc.c.mesh.gdf.imatrix_as_array(global_cos=global_cos)
        femesh = tri.Triangulation(x, y, np.asarray(imat))

        # get values and generate polygons from matplotlib (suppress output)
        values = self._get_nodal_values(item)
        fig, ax = plt.subplots(1, 1)
        fringes = ax.tricontourf(femesh, values, cmap='rainbow')
        _ = ax.remove()

        # create geodataframe from fringes
        p = []
        for collection in fringes.collections:
            for path in collection.get_paths():
                for polygon in path.to_polygons():
                    p.append(Polygon(polygon))
        gdf = gpd.GeoDataFrame(p)
        gdf.columns = ["geometry"]
        gdf.set_geometry("geometry", inplace=True)
        gdf[str(item)+"_min"] = fringes.levels[:-1]
        gdf[str(item)+"_max"] = fringes.levels[1:]

        return gdf

    def isolines(self, item, subitem=0, global_cos=True):
        """
        Get isocontour lines.
        :param global_cos: If True, use global coordinate system (default: local)
        :return: GeoDataFrame
        """

        import geopandas as gpd
        from shapely.geometry import LineString
        import numpy as np
        import matplotlib.pyplot as plt
        import matplotlib.tri as tri

        # read incidence matrix and node values
        x, y, imat = self.doc.c.mesh.gdf.imatrix_as_array(global_cos=global_cos)
        femesh = tri.Triangulation(x, y, np.asarray(imat))

        # get values and generate polygons from matplotlib (suppress output)
        values = self._get_nodal_values(item)
        fig, ax = plt.subplots(1, 1)
        fringes = ax.tricontour(femesh, values, cmap='rainbow')
        _ = ax.remove()

        # create geodataframe from contours
        p = []
        for collection in fringes.collections:
            for path in collection.get_paths():
                for polygon in path.to_polygons(closed_only=False):
                    p.append(LineString(polygon))
        gdf = gpd.GeoDataFrame(p)
        gdf.columns = ["geometry"]
        gdf.set_geometry("geometry", inplace=True)
        gdf[str(item)] = fringes.levels

        return gdf
