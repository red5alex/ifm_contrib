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
        :param tricontourset: The contourset to convert
        :type tricontourset: matplotlib.tri.tricontour.TriContourSet
        :param itemname: attribute name of the column(s) in the GeoDataFrame
        :type itemname: str

        :return: geodataframe
        :rtype: GeoPandas.GeoDataFrame
        """

        import geopandas as gpd
        from shapely.geometry import Polygon, MultiPolygon, LineString

        if tricontourset.filled:
            #### POLYGON TYPE COLLECTION ####

            shapes = []
            for polycollection in tricontourset.collections:
                polygons = []
                #assert len(collection.get_paths()) == 1, "more than one path found"
                for path in polycollection.get_paths():
                    for polygon in path.to_polygons():
                        polygons.append(Polygon(polygon))
                shapes.append(MultiPolygon(polygons))

            # create new dataframe
            gdf = gpd.GeoDataFrame()

            # use fringes as geometry
            gdf["geometry"] = shapes
            gdf.set_geometry("geometry", inplace=True)

            # add limits and layers to gdf
            gdf["layer"] = tricontourset.layers
            gdf[str(itemname) + "_min"] = tricontourset.levels[:-1]
            gdf[str(itemname) + "_max"] = tricontourset.levels[1:]

        else:
            #### Line-Type Collection ###

            shapes = []
            levels = []
            layers = []

            for level, collection, layer in zip(tricontourset.levels, tricontourset.collections, tricontourset.layers):
                for path in collection.get_paths():
                    linestring = LineString([seg[0] for seg in path.iter_segments()])

                    shapes.append(linestring)
                    levels.append(level)
                    layers.append(layer)

            gdf = gpd.GeoDataFrame(geometry=shapes)
            gdf["itemname"] = levels
            gdf["layer"] = layers

        # set a coordinate system if defined for the model
        if self.doc.c.crs is not None:
            gdf.crs = self.doc.c.crs

        return gdf


    def fringes(self, attribute_name=None, suppress_output=True, *args, **kwargs):
        """
        Create fringes polygons of a given nodal parameter, expression or distribution. Return the plot as a polygonal
        GeoDataFrame.

        :return:           geopandas.GeoDataFrame
        """
        import matplotlib.pyplot as plt

        # Attribute name is taken from the keyword argument dict ('par', 'distr' or 'expr') if not explicitely given
        # Error if it does not exist

        for kwargname in ["par", "distr", "expr"]:
            if kwargname in kwargs.keys():
                attribute_name = kwargs[kwargname]
        if attribute_name is None:
            raise ValueError("must provide an attribute name if par, distr or expr not given")

        # get the contourplot but suppress output
        contourset = self.doc.c.plot.fringes(*args, **kwargs)
        if suppress_output:
            plt.close()

        # convert to GeoDatFrame
        return self._tricontourset_to_gdf(contourset, itemname=attribute_name)

    def isolines(self, attribute_name=None, suppress_output=True, *args, **kwargs):
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

        import matplotlib.pyplot as plt

        # Attribute name is taken from the keyword argument dict ('par', 'distr' or 'expr') if not explicitely given
        # Error if it does not exist

        for kwargname in ["par", "distr", "expr"]:
            if kwargname in kwargs.keys():
                attribute_name = kwargs[kwargname]
        if attribute_name is None:
            raise ValueError("must provide an attribute name if par, distr or expr not given")

        # get the contourplot but suppress output
        contourset = self.doc.c.plot.isolines(*args, **kwargs)
        if suppress_output:
            plt.close()

        # convert to GeoDatFrame
        return self._tricontourset_to_gdf(contourset, itemname=attribute_name)
