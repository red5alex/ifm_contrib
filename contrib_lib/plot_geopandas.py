from ifm import Enum


class PlotGpd:
    """
    Functions for exporting plotted data like isocontours as GeoDataFrame. Results are similar to the
    output of the View Components Panel of the FEFLOW GUI.
    """

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

        # set a coordinate system if defined for the model
        if self.doc.c.crs is not None:
            gdf.crs = self.doc.c.crs

        return gdf

    def fringes(self, par=None, expr=None, distr=None, slice=1, global_cos=True, levels=None, species=None):
        """
        Create fringes polygons of a given nodal parameter, expression or distribution. Return the plot as a polygonal
        GeoDataFrame.

        :param par:        Type of parameter to evaluate. Parameter are provided as ifm.Enum.
        :type par:         ifm.Enum
        :param distr:      Name of user distribution to evaluate.
        :type distr:       str
        :param expr:       Name of user expression to evaluate.
        :type expr:        str
        :param slice:      if provided in a 3D model, create fringe polygons on this slice.
        :type layer:       int
        :param global_cos: If True, use global coordinate system (default: local)
        :type global_cos:  bool
        :return:           geopandas.GeoDataFrame
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


    def isolines(self, par=None, expr=None, distr=None, slice=1, global_cos=True, levels=None, species=None):
        """
        Create isolines of a given nodal parameter, expression or distribution. Return the plot as a LineString geometry-type
        GeoDataFrame.

        :param par:        Type of parameter to evaluate. Parameter are provided as ifm.Enum.
        :type par:         ifm.Enum
        :param distr:      Name of user distribution to evaluate.
        :type distr:       str
        :param expr:       Name of user expression to evaluate.
        :type expr:        str
        :param slice:      if provided in a 3D model, create isolines on this slice.
        :type layer:       int
        :param global_cos: If True, use global coordinate system (default: local)
        :type global_cos:  bool
        :return:           geopandas.GeoDataFrame
        """

        import geopandas as gpd
        from shapely.geometry import LineString
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
            isolines = ax.tricontour(femesh, values,)
        else:
            isolines = ax.tricontour(femesh, values, levels)
        _ = ax.remove()
        plt.close()  # this is important to prevent a memory leak!

        # create geodataframe from contours
        p = []
        levels = []
        for level, collection in zip(isolines.levels, isolines.collections):
            for path in collection.get_paths():
                for polygon in path.to_polygons(closed_only=False):
                    p.append(LineString(polygon))
                    levels.append(level)
        gdf = gpd.GeoDataFrame(p)

        if len(gdf) > 0:
            gdf.columns = ["geometry"]
        else:
            gdf["geometry"] = []

        gdf.set_geometry("geometry", inplace=True)
        gdf[str(par)] = levels

        # set a coordinate system if defined for the model
        if self.doc.c.crs is not None:
            gdf.crs = self.doc.c.crs

        return gdf
