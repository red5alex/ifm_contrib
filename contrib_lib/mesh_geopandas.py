from ifm import Enum

class MeshGpd:

    def __init__(self, doc):
        self.doc = doc


    def elements(self, par=None, expr=None, distr=None, global_cos=True, layer=None, selection=None, as_2d=False):
        """
        Get the mesh as a GeoPandas GeoDataFrame.
        :param par: Dict {colname : parid} or List [parid]. Adds values of given parameters as columns.
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

        if par is not None:
            # single items become lists
            if type(par) == int:
                par = [par]

            # export parameters if provided
            if type(par) == list:
                for parameter_id in par:
                    self.doc.getParamSize(parameter_id)
                    gdf_elements[parameter_id] = self.doc.getParamValues(parameter_id)

            if type(par) == dict:
                for key in par:
                    self.doc.getParamSize(par[key])
                    gdf_elements[key] = self.doc.getParamValues(par[key])

        if expr is not None:
            # single items become lists
            if type(expr) == str:
                expr = [expr]

            for x in expr:
                if type(x) == str:
                    exprID = self.doc.getElementalExprDistrIdByName(x)
                elif type(x) == int:
                    exprID = x
                else:
                    raise ValueError("expr must be string (for name) or integer (for id)")
                gdf_elements[x] = [self.doc.getElementalExprDistrValue(exprID, n) for n in
                                  range(self.doc.getNumberOfElements())]

        if distr is not None:
            # single items become lists
            if type(distr) == str:
                distr = [distr]

            for d in distr:
                if type(d) == str:
                    distrID = self.doc.getElementalRefDistrIdByName(d)
                elif type(d) == int:
                    distrID = d
                else:
                    raise ValueError("expr distr be string (for name) or integer (for id)")
                gdf_elements[d] = self.doc.getElementalRefDistrValues(distrID)

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


    def nodes(self, *args, **kwargs):
        """
        Create a geopandas.GeoDataFrame of the nodes.
        Can use all parameters of doc.c.mesh.df.nodes().
        :return: geopandas.GeoDataFrame
        """
        from shapely.geometry import Point
        df_nodes = self.doc.c.mesh.df.nodes(*args, **kwargs)
        df_nodes["element_shape"] = [Point(row.X, row.Y) for (i, row) in df_nodes.iterrows()]
        return df_nodes.set_geometry("element_shape")


    def model_area(self):
        df = self.doc.c.mesh.df.elements(layer=1, as_2d=True)
        df = df.dissolve(by="LAYER")
        df.reset_index(inplace=True)
        del (df["ELEMENT"])
        del (df["LAYER"])
        del (df["TOP_ELEMENT"])
        df["AREA"] = df.geometry.area
        return df
