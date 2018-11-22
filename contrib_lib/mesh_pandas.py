from ifm import Enum


class MeshPd:

    def __init__(self, doc):
        self.doc = doc

    def elements(self, parameters=None, global_cos=True, layer=None, selection=None, as_2d=False):
        """
        Get the mesh as a GeoPandas GeoDataFrame.
        :param parameters: Dict {colname : parid} or List [parid]. Adds values of given parameters as columns.
        :param global_cos: If True, use global coordinate system (default: local)
        :return: GeoDataFrame
        """

        import pandas as pd

        # create a GeoDataFrame from the mesh
        df_elements = pd.DataFrame(index=range(self.doc.getNumberOfElements()))
        df_elements.index.name = "ELEMENT"
        # df_elements["ELEMENT"] = df_elements.index.values
        df_elements["LAYER"] = df_elements.index.values / self.doc.getNumberOfElementsPerLayer() + 1
        df_elements["TOP_ELEMENT"] = df_elements.index.values % self.doc.getNumberOfElementsPerLayer()

        # export parameters if provided
        if type(parameters) == list:
            for parameter_id in parameters:
                self.doc.getParamSize(parameter_id)
                df_elements[parameter_id] = self.doc.getParamValues(parameter_id)

        if type(parameters) == dict:
            for key in parameters:
                self.doc.getParamSize(parameter_id)
                df_elements[key] = self.doc.getParamValues(parameters[key])

        # filter by given selection
        if selection is not None:
            sele = self.doc.c.sel.set(selection)
            sele = sele.intersection(set(df_elements.index))
            df_elements = df_elements.iloc[list(sele)]

        # filter
        if layer is not None:
            # if only single layer requested, create list with one element
            if type(layer) == int:
                layer = [layer]
            # filter by layer list
            df_elements = df_elements.loc[df_elements.LAYER.isin(layer)]

        return df_elements
