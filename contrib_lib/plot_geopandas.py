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

    def _tricontourset_to_gdf(self, tricontourset, itemname):
        """
        Create a GeoPandas.GeoDataFrame from a TriContourSet object
        :return: geodataframe
        """

        import geopandas as gpd
        from shapely.geometry import Polygon, MultiPolygon

        # create list of Multipolygons from contourset
        fringes_multipolygons = []
        for collection in tricontourset.collections:
            polygons = []
            assert len(collection.get_paths()) == 1, "more than one path found"
            for path in collection.get_paths():
                for polygon in path.to_polygons():
                    polygons.append(Polygon(polygon))
            fringes_multipolygons.append(MultiPolygon(polygons))

        # create new dataframe
        gdf = gpd.GeoDataFrame()

        # use fringes as geometry
        gdf["geometry"] = fringes_multipolygons
        gdf.set_geometry("geometry", inplace=True)

        # add limits and layers to gdf
        gdf["layer"] = tricontourset.layers
        gdf[str(itemname) + "_min"] = tricontourset.levels[:-1]
        gdf[str(itemname) + "_max"] = tricontourset.levels[1:]

        return gdf

    def fringes(self, par=None, expr=None, distr=None, slice=1, global_cos=True, levels=None, species=None):
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

        # set current species
        if species is not None:
            if type(species) == str:
                speciesID = self.doc.findSpecies(species)
            elif type(species) == int:
                speciesID = species
            else:
                raise ValueError("species must be string (for name) or integer (for id)")
            self.doc.setMultiSpeciesId(speciesID)

        # read incidence matrix and node coordinates
        imat = self.doc.c.mesh.get_imatrix2d(slice=slice, ignore_inactive=True, split_quads_to_triangles=True)
        x, y = self.doc.getParamValues(Enum.P_MSH_X), self.doc.getParamValues(Enum.P_MSH_Y)

        if global_cos:
            X0 = self.doc.getOriginX()
            Y0 = self.doc.getOriginY()
            x = [X + X0 for X in x]
            y = [Y + Y0 for Y in y]

        # create Triangulation object
        femesh = tri.Triangulation(x, y, np.asarray(imat))

        # get values, remove nan values (=inactive elements)
        if par is not None:
            values = self.doc.getParamValues(par)
        elif expr is not None:
            if type(expr) == str:
                exprID = self.doc.getNodalExprDistrIdByName(expr)
            elif type(expr) == int:
                exprID = expr
            else:
                raise ValueError("expr must be string (for name) or integer (for id)")
            values = [self.doc.getNodalExprDistrValue(exprID, n) for n in range(self.doc.getNumberOfNodes())]
        elif distr is not None:
            if type(distr) == str:
                distrID = self.doc.getNodalRefDistrIdByName(distr)
            elif type(distr) == int:
                distrID = distr
            else:
                raise ValueError("distr must be string (for name) or integer (for id)")
            values = [self.doc.getNodalRefDistrValue(distrID, n) for n in range(self.doc.getNumberOfNodes())]
        else:
            raise ValueError("either of parameter item, expr or distr must be provided!")

        # set nan values to zero
        values = np.nan_to_num(np.asarray(values))

        # generate polygons from matplotlib (suppress output)
        fig, ax = plt.subplots(1, 1, figsize=(0,0))
        if levels is None:
            fringes = ax.tricontourf(femesh, values,)
        else:
            fringes = ax.tricontourf(femesh, values, levels)
        _ = ax.remove()
        plt.close()  # this is important to prevent a memory leak!

        return self._tricontourset_to_gdf(fringes, itemname=par)



    def isolines(self, par, subitem=0, global_cos=True):
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
        values = self.doc.getParamValues(par)
        fig, ax = plt.subplots(1, 1)
        fringes = ax.tricontour(femesh, values, cmap='rainbow')
        _ = ax.remove()
        plt.close()  # this is important to prevent a memory leak!

        # create geodataframe from contours
        p = []
        for collection in fringes.collections:
            for path in collection.get_paths():
                for polygon in path.to_polygons(closed_only=False):
                    p.append(LineString(polygon))
        gdf = gpd.GeoDataFrame(p)
        gdf.columns = ["geometry"]
        gdf.set_geometry("geometry", inplace=True)
        gdf[str(par)] = fringes.levels

        return gdf
