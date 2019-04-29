from ifm import Enum
import numpy as np


class MeshPd:
    """
    Functions for exporting nodal and elemental properties to DataFrames.
    """

    def __init__(self, doc):
        self.doc = doc

    def elements(self, par=None, expr=None, distr=None, layer=None, selection=None, as_2d=False):
        """
        Create a Pandas Dataframe with information on the model elements.

        :param par:        Create additional columns with parameter values. Parameter are provided as ifm.Enum. Multiple
                           columns are created if a list is provided.  Columns can be givens custom names if a dict
                           {column name : parid} is provided.
        :type par:         dict, list or ifm.Enum
        :param distr:      Name or list of names of user distributions. For each uer distribution provided, a column with
                           with distribution values will be added to the DataFrame.
        :type distr:       str or list
        :param expr:       Name or list of names of user expressions. For each uer expression provided, a column with
                           with distribution values will be added to the DataFrame.
        :type expr:        str or list
        :param layer:      if provided in a 3D model, return only elements of this layer
        :type layer:       int
        :param selection:  if provided in a 3D model, return only elements of this selection
        :type selection:   str
        :return:           pandas.DataFrame
        """

        import pandas as pd

        # create a GeoDataFrame from the mesh
        df_elements = pd.DataFrame(index=range(self.doc.getNumberOfElements()))
        df_elements.index.name = "ELEMENT"
        # df_elements["ELEMENT"] = df_elements.index.values
        df_elements["LAYER"] = df_elements.index.values / self.doc.getNumberOfElementsPerLayer() + 1
        df_elements["TOP_ELEMENT"] = df_elements.index.values % self.doc.getNumberOfElementsPerLayer()

        if par is not None:
            # single items become lists
            if type(par) == int:
                par = [par]

            # export parameters if provided
            if type(par) == list:
                for parameter_id in par:
                    self.doc.getParamSize(parameter_id)
                    df_elements[parameter_id] = self.doc.getParamValues(parameter_id)

            if type(par) == dict:
                for key in par:
                    self.doc.getParamSize(par[key])
                    df_elements[key] = self.doc.getParamValues(par[key])

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
                df_elements[x] = [self.doc.getElementalExprDistrValue(exprID, n) for n in range(self.doc.getNumberOfElements())]

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
                df_elements[d] = self.doc.getElementalRefDistrValues(distrID)

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
        Create a Pandas Dataframe with information on the model nodes.

        :param par:        Create additional columns with parameter values. Parameter are provided as ifm.Enum. Multiple
                           columns are created if a list is provided.  Columns can be givens custom names if a dict
                           {column name : parid} is provided.
        :type par:         dict, list or ifm.Enum
        :param distr:      Name or list of names of user distributions. For each uer distribution provided, a column with
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
        :return:           pandas.DataFrame
        """

        import pandas as pd

        # create a GeoDataFrame from the mesh
        df_nodes = pd.DataFrame(index=range(self.doc.getNumberOfNodes()))
        df_nodes.index.name = "NODE"
        # df_elements["ELEMENT"] = df_elements.index.values
        df_nodes["SLICE"] = df_nodes.index.values / self.doc.getNumberOfNodesPerSlice() + 1
        df_nodes["TOP_NODE"] = df_nodes.index.values % self.doc.getNumberOfNodesPerSlice()

        if global_cos:
            X0, Y0 = self.doc.getOriginX(), self.doc.getOriginY()
        else:
            X0, Y0 = 0, 0
        df_nodes["X"] = np.array(self.doc.getParamValues(Enum.P_MSH_X)) + X0
        df_nodes["Y"] = np.array(self.doc.getParamValues(Enum.P_MSH_Y)) + Y0

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
                if exprID == -1:
                    raise ValueError("Expression "+str(x)+" not found!")

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
                slice = [slice]
            # filter by layer list
            df_nodes = df_nodes.loc[df_nodes.SLICE.isin(slice)]

        return df_nodes.replace(-99999.0, np.nan)

    def get_available_items(self, Type=None):
        #TODO: Generalize and move to Enum!

        import pandas as pd

        available_items = []
        for e in [e for e in dir(Enum) if "P_" in e]:
            e_num = eval("Enum." + e)
            try:
                ii = self.doc.getParamSize(e_num)
                if ii == self.doc.getNumberOfNodes()  and ii == self.doc.getNumberOfElements():
                    itemtype = 'ambiguous'  # n_nodes = n_elements, can't determine type
                elif ii == self.doc.getNumberOfNodes():
                    itemtype = 'nodal'
                elif ii == self.doc.getNumberOfElements():
                    itemtype = 'elemental'
                else:
                    itemtype = 'unknowm'
                available_items.append((e, e_num, itemtype))
            except StandardError:
                pass

        df_items = pd.DataFrame(available_items, columns=["Name", "Enum_Constant", "Type"])

        # filter by type
        if Type is not None:
            df_items = df_items[df_items.Type == Type]

        df_items.set_index("Enum_Constant", inplace=True)

        return df_items