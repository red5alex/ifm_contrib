from ifm import Enum
import numpy as np


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

        return df_elements.replace(-99999.0, np.nan)

    def nodes(self, par=None, expr=None, distr=None, global_cos=True, slice=None, selection=None):
        """
        Get the mesh as a GeoPandas GeoDataFrame.
        :param par: Dict {colname : parid} or List [parid]. Adds values of given parameters as columns.
        :param global_cos: If True, use global coordinate system (default: local)
        :return: GeoDataFrame
        """

        import pandas as pd

        # create a GeoDataFrame from the mesh
        df_nodes = pd.DataFrame(index=range(self.doc.getNumberOfNodes()))
        df_nodes.index.name = "NODE"
        # df_elements["ELEMENT"] = df_elements.index.values
        df_nodes["SLICE"] = df_nodes.index.values / self.doc.getNumberOfNodesPerSlice() + 1
        df_nodes["TOP_NODE"] = df_nodes.index.values % self.doc.getNumberOfNodesPerSlice()

        if par is not None:
            # single items become lists
            if type(par) == int:
                par = [par]

            # export parameters if provided
            if type(par) == list:
                for parameter_id in par:
                    self.doc.getParamSize(parameter_id)
                    df_nodes[parameter_id] = self.doc.getParamValues(parameter_id)

            if type(par) == dict:
                for key in par:
                    self.doc.getParamSize(par[key])
                    df_nodes[key] = self.doc.getParamValues(par[key])

        if expr is not None:
            # single items become lists
            if type(expr) == str:
                expr = [expr]

            for x in expr:
                if type(x) == str:
                    exprID = self.doc.getNodalExprDistrIdByName(x)
                elif type(x) == int:
                    exprID = x
                else:
                    raise ValueError("expr must be string (for name) or integer (for id)")
                df_nodes[x] = [self.doc.getNodalExprDistrValue(exprID, n) for n in range(self.doc.getNumberOfNodes())]

        if distr is not None:
            # single items become lists
            if type(distr) == str:
                distr = [distr]

            for d in distr:
                if type(d) == str:
                    distrID = self.doc.getNodalRefDistrIdByName(d)
                elif type(d) == int:
                    distrID = d
                else:
                    raise ValueError("expr distr be string (for name) or integer (for id)")
                df_nodes[d] = self.doc.getNodalRefDistrValues(distrID)

        # filter by given selection
        if selection is not None:
            sele = self.doc.c.sel.set(selection)
            sele = sele.intersection(set(df_nodes.index))
            df_nodes = df_nodes.iloc[list(sele)]

        # filter
        if slice is not None:
            # if only single slice requested, create list with one element
            if type(slice) == int:
                layer = [slice]
            # filter by layer list
            df_nodes = df_nodes.loc[df_nodes.LAYER.isin(slice)]

        return df_nodes.replace(-99999.0, np.nan)
