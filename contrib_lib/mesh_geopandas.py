from ifm import Enum


class MeshGpd:
    """
    Functions to obtain data of FEFLOWs Data Panel as geopandas.GeoDataFrames.
    """

    def __init__(self, doc):
        self.doc = doc

    def elements(self, par=None, expr=None, distr=None, global_cos=True, layer=None, selection=None, as_2d=False,
                 content=None, polygons_as_2d=False):
        """
        Create a GeoPandas GeoDataframe with information on the model elements.

        :param par:        Create additional columns with parameter values. Parameter are provided as ifm.Enum. Multiple
                           columns are created if a list is provided.  Columns can be givens custom names if a dict
                           {column name : parid} is provided.
        :type par:         dict, list or ifm.Enum
        :param distr:      Name or list of names of user distributions. For each uer distribution provided, a column
                           with distribution values will be added to the DataFrame.
        :type distr:       str or list
        :param expr:       Name or list of names of user expressions. For each uer expression provided, a column with
                           with distribution values will be added to the DataFrame.
        :type expr:        str or list
        :param global_cos: If True (default), use global instead of local coordinate system.
        :type global_cos:  bool
        :param layer:      if provided in a 3D model, return only elements of this layer
        :type layer:       int
        :param selection:  if provided in a 3D model, return only elements of this selection
        :type selection:   str
        :return:           geopandas.GeoDataFrame
        """

        import geopandas as gpd
        from shapely.geometry import Polygon
        import numpy as np

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
        if polygons_as_2d:
            gdf_elements = gpd.GeoDataFrame([Polygon([(x[n], y[n]) for n in element[:len(element)//2]]) for element in imat])
        else:
            gdf_elements = gpd.GeoDataFrame([Polygon([(x[n], y[n]) for n in element]) for element in imat])

        gdf_elements.columns = ["element_shape"]
        gdf_elements.set_geometry("element_shape", inplace=True)
        gdf_elements.index.name = "ELEMENT"
        gdf_elements["ELEMENT"] = gdf_elements.index.values
        gdf_elements["LAYER"] = gdf_elements.index.values // self.doc.getNumberOfElementsPerLayer() + 1
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
                if layer is None:
                    values = self.doc.getElementalRefDistrValues(distrID)
                else:
                    ee = self.doc.getNumberOfElementsPerLayer()
                    values = self.doc.getElementalRefDistrValues(distrID)[ee*(layer-1):ee*layer]
                gdf_elements[d] = values

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

        # set a coordinate system if defined for the model
        if self.doc.c.crs is not None:
            gdf_elements.crs = self.doc.c.crs

        # add elemental content
        if content is not None and content is not False:
            if type(content) == list:
                items = content
            elif type(content) == bool and content is True:
                items = [int(i) for i in self.doc.c.content.df.info().index]
            elif type(content) == int:
                items = [content]
            else:
                raise ValueError("content must be None, False, True, int or list[int]")

            for i, row in self.doc.c.content.df.info().loc[items].iterrows():
                name = row["ifm.Enum"]
                try:
                    gdf_elements[name] = [self.doc.getElementalContent(i, e) for e in gdf_elements.index]
                except RuntimeError:
                    gdf_elements[name] = np.nan


        return gdf_elements

    def nodes(self, *args, **kwargs):
        """
        Create a Pandas Dataframe with information on the model nodes.

        :param par:        Create additional columns with parameter values. Parameter are provided as ifm.Enum. Multiple
                           columns are created if a list is provided.  Columns can be givens custom names if a dict
                           {column name : parid} is provided.
        :type par:         dict, list or ifm.Enum
        :param distr:      Name or list of names of user distributions. For each uer distribution provided, a column
                           with distribution values will be added to the DataFrame.
        :type distr:       str or list
        :param expr:       Name or list of names of user expressions. For each uer expression provided, a column with
                           with distribution values will be added to the DataFrame.
        :type expr:        str or list
        :param global_cos: if True (default), use global instead of local coordinate system
        :type global_cos:  bool
        :param slice:      if provided in a 3D model, return only nodes of this slice
        :type slice:       int
        :param selection:  if provided, return only nodes of this selection
        :type selection:   str
        :return:           geopandas.GeoDataFrame
        """

        from shapely.geometry import Point
        import geopandas as gpd  # required, this integrates the df.set_geometry function in pandas.DataFrame

        df_nodes = self.doc.c.mesh.df.nodes(*args, **kwargs)
        df_nodes["element_shape"] = [Point(row.X, row.Y) for (i, row) in df_nodes.iterrows()]

        gdf_nodes = df_nodes.set_geometry("element_shape")

        # set a coordinate system if defined for the model
        if self.doc.c.crs is not None:
            gdf_nodes.crs = self.doc.c.crs

        return gdf_nodes

    def border_nodes(self, border_number=0, *args, **kwargs):
        from shapely.geometry import Point
        import geopandas as gpd
        gdf_border = gpd.GeoDataFrame(self.doc.c.mesh.df.border_nodes(border_number, *args, **kwargs))
        gdf_border["geometry"] = gdf_border.apply(lambda x: Point(x.X, x.Y), axis=1)
        return gdf_border

    def borders(self):
        """
        Return a GeoDataFrame with all model borders.

        :return:
        :rtype: shapely.geometry.LinearRing
        """
        import geopandas as gpd
        from shapely.geometry import LinearRing

        borders = self.doc.c.mesh.get_borders()
        shapes = []
        for border in self.doc.c.mesh.get_borders():
            gdf_nodes = self.doc.c.mesh.gdf.nodes(selection=borders[border])
            outline = LinearRing(list(gdf_nodes.element_shape))
            shapes.append(outline)

        # create GeoDataFrame
        gdf_borders = gpd.GeoDataFrame(geometry=shapes)
        gdf_borders.index.name = "BorderIndex"

        # add useful information
        gdf_borders["is_exterior"] = [self.doc.isExteriorBorder(b) == 1 for b in borders]
        gdf_borders["is_interior"] = [self.doc.isExteriorBorder(b) == 0 for b in borders]
        gdf_borders["node_count"] = [len(borders[nn]) for nn in borders]
        gdf_borders["LENGTH"] = gdf_borders.geometry.length

        # set a coordinate system if defined for the model
        if self.doc.c.crs is not None:
            gdf_borders.crs = self.doc.c.crs

        return gdf_borders


    def model_area(self, selection=None):
        """
        Get the model area as a single 2D polygon.

        :param selection:  if provided, return model area related to this elemental selection.
        :type selection: str

        :return: geopandas.GeoDataFrame.
        """
        import geopandas as gpd
        from shapely.geometry import Polygon

        if selection is None:
            # Create a GeoDataFrame of Model area based on Border Nodes API.
            # This is generally fast but does not allow to create the polygons based on selections.

            # create areas from outer borders:
            gdf_borders = self.doc.c.mesh.gdf.model_borders()
            holes = gdf_borders[gdf_borders.is_interior].geometry

            areas = [Polygon(shell=row.geometry, holes=holes) for i, row in
                     gdf_borders[gdf_borders.is_exterior].iterrows()]

            # create GeoData Frame
            gdf_areas = gpd.GeoDataFrame(geometry=areas)

            # add useful information
            gdf_areas["Outer_BorderIndex"] = gdf_borders[gdf_borders.is_exterior].index
            gdf_areas["AREA"] = gdf_areas.geometry.area

        else:
            if self.doc.pdoc.findSelection(Enum.SEL_ELEMENTAL, selection) == -1:
                raise ValueError("Elemental Selection {} does not exist".format(selection))

            gdf_areas = self.doc.c.mesh.gdf.elements(layer=1, as_2d=True, selection=selection)
            gdf_areas["dummy"] = 0
            gdf_areas = gdf_areas.dissolve(by="dummy")
            gdf_areas.reset_index(inplace=True)
            del (gdf_areas["ELEMENT"])
            del (gdf_areas["LAYER"])
            del (gdf_areas["TOP_ELEMENT"])
            del (gdf_areas["dummy"])
            gdf_areas["AREA"] = gdf_areas.geometry.area

        # set a coordinate system if defined for the model
        if self.doc.c.crs is not None:
            gdf_areas.crs = self.doc.c.crs

        return gdf_areas

    def mlw(self, global_cos=True):
        """
        Return a geoPandas.GeoDataFrame with information on all Multi-Layer wells in the model.
        :return:
        """
        from shapely.geometry import Point
        import geopandas as gpd
        gdf = gpd.GeoDataFrame(self.doc.c.mesh.df.mlw(global_cos=global_cos))

        # set a coordinate system if defined for the model
        if self.doc.c.crs is not None:
            gdf.crs = self.doc.c.crs

        gdf["element_shape"] = [Point(row.bottom_x, row.bottom_y) for (i, row) in gdf.iterrows()]
        return gdf.set_geometry("element_shape")

    def dfe(self):
        """
        Return a geoPandas.GeoDataFrame with information on all DFE in the model.
        :return:
        """
        if self.doc.getNumberOfDimensions() != 3:
            raise NotImplementedError("this function is currently only available for 3D problems")

        from shapely.geometry import LineString
        import geopandas as gpd
        import numpy as np

        gdf = gpd.GeoDataFrame(self.doc.c.mesh.df.dfe())

        # get coordinates of nodes
        df_nodes = self.doc.c.mesh.df.nodes(par={"Z": Enum.P_ELEV})
        gdf["x1"] = np.array(df_nodes.loc[gdf.node_1].X)
        gdf["x2"] = np.array(df_nodes.loc[gdf.node_2].X)
        gdf["y1"] = np.array(df_nodes.loc[gdf.node_1].Y)
        gdf["y2"] = np.array(df_nodes.loc[gdf.node_2].Y)
        gdf["z1"] = np.array(df_nodes.loc[gdf.node_1].Z)
        gdf["z2"] = np.array(df_nodes.loc[gdf.node_2].Z)

        gdf["element_shape"] = [LineString([(row.x1, row.y1, row.z1),
                                            (row.x2, row.y2, row.z2)]) for (i, row) in gdf.iterrows()]

        gdf.drop(columns=["x1", "x2", "y1", "y2", "z1", "z2"], inplace=True)

        # set a coordinate system if defined for the model
        if self.doc.c.crs is not None:
            gdf.crs = self.doc.c.crs

        return gdf.set_geometry("element_shape")
