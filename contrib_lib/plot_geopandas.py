from ifm import Enum


class PlotGpd:

    def __init__(self, doc):
        self.doc = doc

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

        def get_nodal_values(doc, item=item):
            """
            get array of nodal heads
            """

            # get range of nodes (2D, 3D)
            # TODO: Support for inactive elements
            if doc.getNumberOfDimensions() == 2:
                nodes = range(doc.getNumberOfNodes())
            else:
                nodes = range(doc.getNumberOfNodesPerSlice())

            # read values into array
            if item == "Head":
                values = [self.doc.getResultsFlowHeadValue(n) for n in nodes]
            else:
                raise NotImplementedError("value "+str(item)+" not implemented")
            # TODO: Implement item, subitem (e.g., Mass, species=1)
            values = np.array(values)

            # replace nan heads (inactive nodes) with mean value
            inds = np.where(np.isnan(values))
            h_mean = values[~np.isnan(values)].mean()
            for i in inds:
                values[i] = h_mean

            return values

        # read incidence matrix and node values
        x, y, imat = self.doc.c.mesh.gdf.imatrix_as_array(global_cos=global_cos)
        femesh = tri.Triangulation(x, y, np.asarray(imat))

        # get values and generate polygons from matplotlib (suppress output)
        values = get_nodal_values(self.doc, item)
        fig, ax = plt.subplots(1, 1)
        fringes = ax.tricontourf(femesh, values, cmap='rainbow')
        _ = ax.remove()

        # create geodataframe from fringes
        p = []
        for collection in fringes.collections:
            for path in collection.get_paths():
                for polygon in path.to_polygons():
                    p.append(Polygon(polygon))
        gdf_fringes = gpd.GeoDataFrame(p)
        gdf_fringes.columns = ["shape"]
        gdf_fringes.set_geometry("shape", inplace=True)
        gdf_fringes[str(item)+"_min"] = fringes.levels[:-1]
        gdf_fringes[str(item)+"_max"] = fringes.levels[1:]
        # gdf_fringes["Label"] = gdf_fringes.From.astype(str) + " - " + gdf_fringes.To.astype(str)

        return gdf_fringes
