from ifm import Enum


class MeshGpd:

    def __init__(self, doc):
        self.doc = doc


    def getGeoDatframe(self, parameters=None, global_cos=True, ):
        """
        Get the mesh as a GeoPandas GeoDataFrame.
        :param global_cos: If True, use global coordinate system (default: local)
        :return: GeoDataFrame
        """

        import geopandas as gpd
        from shapely.geometry import Point, Polygon

        x, y, imat = self.doc.c.mesh.imatrix_as_array(global_cos=global_cos, layer=0, split_quads_to_triangles=False)
        # create a GeoDataFrame from the mesh and save as shape file
        gdf_elements = gpd.GeoDataFrame([Polygon([(x[n], y[n]) for n in element]) for element in imat])
        gdf_elements.columns = ["element_shape"]
        gdf_elements.set_geometry("element_shape", inplace=True)
        gdf_elements.index.name = "ELEMENT"
        gdf_elements["ELEMENT"] = gdf_elements.index.values
        gdf_elements["AREA"] = gdf_elements.geometry.area

        # export parameters if provided
        if type(parameters) == dict:
            for key in parameters:
                gdf_elements[key] = self.doc.getParamValues(parameters[key])

        return gdf_elements
