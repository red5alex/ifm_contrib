from ifm import Enum


class ObsGpd:

    def __init__(self, doc):
        self.doc = doc

    def getGeoDataframe(self, global_cos=True):
        """
        Get the observation points as a GeoPandas GeoDataFrame.
        :param global_cos: If True, use global coordinate system (default)
        :return: GeoDataFrame
        """

        import geopandas as gpd
        from shapely.geometry import Point, Polygon
        import numpy as np

        # create a list of observation points in FEFLOW model:
        obs = []
        for obsid in range(self.doc.getNumberOfValidObsPoints()):

            # get geometry
            x, y, z = self.doc.getXOfObsId(obsid), self.doc.getYOfObsId(obsid), self.doc.getZOfObsId(obsid)
            if global_cos:
                X0, Y0 = self.doc.getOriginX(), self.doc.getOriginY()
                x += X0
                y += Y0

            shape = Point(x, y)  # create a geometry object

            # get label and append to list
            label = str(self.doc.getObsLabel(obsid))

            # get node number and append to list (None for arbitrary-type observation point)
            node = self.doc.getTypeOfObsId(obsid)
            if node < 0:
                node = np.nan

            # get modelled values
            h = self.doc.getFlowValueOfObsIdAtCurrentTime(obsid)

            obs.append([obsid, label, x, y, z, node, h, shape])

        # create and return dataframe
        gdf_obs = gpd.GeoDataFrame(obs, columns=["id", "label", "x", "y", "z", "node", "h", "shape"])
        gdf_obs.set_index("id", inplace=True)
        gdf_obs.set_geometry("shape", inplace=True)

        return gdf_obs
