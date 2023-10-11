from ifm import Enum


class ObsGpd:
    """
    Functions to obtain data of Observation Points as geoPandas.GeoDataFrames.
    """

    def __init__(self, doc):
        self.doc = doc

    def obspoints(self, global_cos=True, filter_by=None):
        """
        Get the observation points as a GeoPandas GeoDataFrame.

        :param global_cos: If True, use global coordinate system (default)
        :type global_cos: Bool
        :param filter_by: dictionary {str : list} defining a filter. Return only observation points whose attributes
                          defined by the key of the dictionary is member of a list provided as the value.
                          
        :type filter_by: dict {str : list}
        :return: GeoDataFrame
        :rtype: geopandas.GeoDataFrame
        """

        import pandas as pd
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

            if self.doc.getNumberOfDimensions() == 2:
                shape = Point(x, y)  # create a 2D geometry object
            elif self.doc.getNumberOfDimensions() == 3:
                shape = Point(x, y, z)  # create a 3D geometry object

            # get label and append to list
            label = str(self.doc.getObsLabel(obsid))

            # get node number and append to list (None for arbitrary-type observation point)
            node = self.doc.getTypeOfObsId(obsid)
            if node < 0:
                node = np.nan

            # get modelled values
            h = self.doc.getFlowValueOfObsIdAtCurrentTime(obsid)

            if self.doc.getProblemClass() in [Enum.PCLS_MASS_TRANSPORT, Enum.PCLS_THERMOHALINE]:
                CONC = self.doc.getMassValueOfObsIdAtCurrentTime(obsid)
            else:
                CONC = np.nan

            obs.append([obsid, label, x, y, z, node, h, CONC, shape])

        # create and return dataframe
        gdf_obs = gpd.GeoDataFrame(obs, columns=["id", "label", "x", "y", "z", "node", "h", "conc", "shape"])

        # set a coordinate system if defined for the model
        if self.doc.c.crs is not None:
            gdf_obs.crs = self.doc.c.crs

        # filter the dataframe by attributes
        if filter_by is not None:
            # check if filter attribute is a dictionary
            if type(filter_by) != dict:
                raise ValueError("filter must be of type dict!")
            for key in filter_by.keys():
                # check if attribute exists
                if key not in gdf_obs.columns:
                    raise ValueError("unknown attribute {}".format(key))
                if type(filter_by[key]) == list:
                    selected_rows = gdf_obs.loc[gdf_obs[key].isin(filter_by[key])]
                    gdf_obs = gpd.GeoDataFrame(selected_rows)
                else:
                    raise ValueError("type {} not supported as dict value! (provide a list)".format(type(filter_by[key])))

        # add reference values for HEAD
        if Enum.P_HEAD in self.doc.c.obs.reference_values.keys():

            # convert dict to dataframe
            df_refvalues = pd.DataFrame(self.doc.c.obs.reference_values[Enum.P_HEAD],
                                        index=self.doc.c.obs.reference_values.keys()).T
            df_refvalues.columns = ["h_obs"]
            gdf_obs = gdf_obs.join(df_refvalues, on="label")

            # calculate residual
            gdf_obs["h_res"] = gdf_obs.h - gdf_obs.h_obs

        # finalize and return
        gdf_obs.set_index("id", inplace=True)
        gdf_obs.set_geometry("shape", inplace=True)
        return gdf_obs
