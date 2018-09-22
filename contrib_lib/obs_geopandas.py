from ifm import Enum


class ObsGpd:

    def __init__(self, doc):
        self.doc = doc

    def getGeoDatframe(self, global_cos=True):
        """
        Get the observation points as a GeoPandas GeoDataFrame.
        :param global_cos: If True, use global coordinate system (default)
        :return: GeoDataFrame
        """

        import geopandas as gpd
        from shapely.geometry import Point, Polygon

        # create a list of observation points in FEFLOW model:
        obs = []
        for o in range(self.doc.getNumberOfValidObsPoints()):

            # get geometry
            x, y, z = self.doc.getXOfObsId(o), self.doc.getYOfObsId(o), self.doc.getZOfObsId(o)
            if global_cos:
                X0, Y0 = self.doc.getOriginX(), self.doc.getOriginY()
                x += X0
                y += Y0

            shape = Point(x, y)  # create a geometry object

            # get label and append to list
            label = self.doc.getObsLabel(o)
            obs.append([label, x, y, z, shape])

        # create and return dataframe
        gdf_obs = gpd.GeoDataFrame(obs, columns=["label", "x", "y", "z", "shape"])
        gdf_obs.set_index("label", inplace=True)
        gdf_obs.set_geometry("shape", inplace=True)

        return gdf_obs
