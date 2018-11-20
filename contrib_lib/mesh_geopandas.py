from ifm import Enum

class MeshGpd:

    def __init__(self, doc):
        self.doc = doc


    def elements(self, parameters=None, global_cos=True, layer=None, selection=None, as_2d=False):
        """
        Get the mesh as a GeoPandas GeoDataFrame.
        :param parameters: Dict {colname : parid} or List [parid]. Adds values of given parameters as columns.
        :param global_cos: If True, use global coordinate system (default: local)
        :return: GeoDataFrame
        """

        import geopandas as gpd
        from shapely.geometry import Polygon

        imat = self.doc.c.mesh.imatrix_as_array(global_cos=global_cos,
                                                split_quads_to_triangles=False,
                                                layer=layer,
                                                as_2d=as_2d)
        if global_cos:
            X0, Y0 = self.doc.getOriginX(), self.doc.getOriginY()
            x = [X + X0 for X in self.doc.getParamValues(Enum.P_MSH_X)]
            y = [Y + Y0 for Y in self.doc.getParamValues(Enum.P_MSH_Y)]
        else:
            x = self.doc.getParamValues(Enum.P_MSH_X)
            y = self.doc.getParamValues(Enum.P_MSH_Y)

        # create a GeoDataFrame from the mesh
        gdf_elements = gpd.GeoDataFrame([Polygon([(x[n], y[n]) for n in element]) for element in imat])
        gdf_elements.columns = ["element_shape"]
        gdf_elements.set_geometry("element_shape", inplace=True)
        gdf_elements.index.name = "ELEMENT"
        gdf_elements["ELEMENT"] = gdf_elements.index.values
        gdf_elements["LAYER"] = gdf_elements.index.values / self.doc.getNumberOfElementsPerLayer() + 1
        gdf_elements["TOP_ELEMENT"] = gdf_elements.index.values % self.doc.getNumberOfElementsPerLayer()
        gdf_elements["AREA"] = gdf_elements.geometry.area

        # export parameters if provided
        if type(parameters) == list:
            for parameter_id in parameters:
                gdf_elements[parameter_id] = self.doc.getParamValues(parameter_id)

        if type(parameters) == dict:
            for key in parameters:
                gdf_elements[key] = self.doc.getParamValues(parameters[key])

        # filter by given selection
        if selection is not None:
            sele = self.doc.c.sel.set(selection)
            sele = sele.intersection(set(gdf_elements.index))
            gdf_elements = gdf_elements.iloc[list(sele)]

        # filter
        if layer is not None:
            # if only single layer requested, create list with one element
            if type(layer) == int:
                layer = [layer]
            # filter by layer list
            gdf_elements = gdf_elements.loc[gdf_elements.LAYER.isin(layer)]


        return gdf_elements

    def model_area(self):
        df = self.doc.c.mesh.df.elements(layer=1, as_2d=True)
        df = df.dissolve(by="LAYER")
        df.reset_index(inplace=True)
        del (df["ELEMENT"])
        del (df["LAYER"])
        del (df["TOP_ELEMENT"])
        df["AREA"] = df.geometry.area
        return df
