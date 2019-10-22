from ifm import Enum
import numpy as np


class MeshPd:
    """
    Functions for exporting nodal and elemental properties to DataFrames.
    """

    def __init__(self, doc):
        self.doc = doc

    def elements(self, par=None, expr=None, distr=None, layer=None, selection=None, centroids=False, content=None):
        """
        Create a Pandas Dataframe with information on the model elements.

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
        :param layer:      if provided in a 3D model, return only elements of this layer
        :type layer:       int
        :param selection:  if provided in a 3D model, return only elements of this selection
        :type selection:   str
        :param centroids:  if True, add coordinates of centroids to DataFrame.
        :type centroids:   bool
        :param content:    Add elemental content to datafrane. see doc.c.conent.df.info for available items.
                           If True, all content items are returned. if int or list(int), specific items are returned.
        :type content:     None, bool, int, list[int]
        :return:           DataFrame, index of element index, all requested information as columns.
        :rtype:            pandas.DataFrame
        """

        import pandas as pd

        # create a GeoDataFrame from the mesh
        df_elements = pd.DataFrame(index=range(self.doc.getNumberOfElements()))
        df_elements.index.name = "ELEMENT"

        if self.doc.getNumberOfNodesPerElement() == 0:  # unstructured mesh
            df_elements["LAYER"] = None
            df_elements["TOP_ELEMENT"] = None
        else:  # assume layered mesh
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
                    if exprID == -1:
                        raise ValueError("expression {} does not exist!".format(str(d)))
                elif type(x) == int:
                    exprID = x
                else:
                    raise ValueError("expr must be string (for name) or integer (for id)")
                df_elements[x] = [self.doc.getElementalExprDistrValue(exprID, n) for n in
                                  range(self.doc.getNumberOfElements())]

        if distr is not None:
            # single items become lists
            if type(distr) == str:
                distr = [distr]

            for d in distr:
                if type(d) == str:
                    distrID = self.doc.getElementalRefDistrIdByName(d)
                    if distrID == -1:
                        raise ValueError("reference distribution {} does not exist!".format(str(d)))
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

        # add centroid values
        if centroids is True:
            df_elements["centroid"] = [self.doc.c.mesh.getCentroid(e) for e in df_elements.index]

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
                    df_elements[name] = [self.doc.getElementalContent(i, e) for e in df_elements.index]
                except StandardError:
                    df_elements[name] = np.nan

        return df_elements.replace(-99999.0, np.nan)

    def nodes(self, par=None, expr=None, distr=None, global_cos=True, slice=None, selection=None, budget=None):
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
        :param budget:     add nodal budget values to dataframe. Can be "flow", "mass", "heat", or a list
                           like ["flow", "mass]. If True, all available budgets will be created. If None, no budget is
                           calculated (default).
        :type budget       bool, str or [str], None.
        :return:           DataFrame, index of element nodes, all requested information as columns.
        :rtype:            pandas.DataFrame
        """

        import pandas as pd

        # create a GeoDataFrame from the mesh
        df_nodes = pd.DataFrame(index=range(self.doc.getNumberOfNodes()))
        df_nodes.index.name = "NODE"

        if self.doc.getNumberOfNodesPerElement() == 0:  # unstructured mesh
            df_nodes["SLICE"] = None
            df_nodes["TOP_NODE"] = None
        else:  # assume layered mesh
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
                    raise ValueError("Expression " + str(x) + " not found!")

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

        # create nodal budgets
        if budget is not None:

            # if a single budget type is provided as str, convert to single-member list first
            if type(budget) == str:
                budget = [budget]

            # if budget is True, create all available budgets
            if budget is True:
                budget = ["flow"]
                if self.doc.pdoc.getProblemClass() in [Enum.PCLS_MASS_TRANSPORT, Enum.PCLS_THERMOHALINE]:
                    budget.append("mass")
                if self.doc.pdoc.getProblemClass() in [Enum.PCLS_HEAT_TRANSPORT, Enum.PCLS_THERMOHALINE]:
                    budget.append("heat")

            # compute nodal values for the flow budget
            if "flow" in budget:
                bdgt = self.doc.budgetFlowCreate()
                df_nodes["budget_flow_bc"] = [self.doc.budgetComponentsQueryFlowAtNode2(bdgt, n)[1] for n in
                                              map(int, df_nodes.index)]
                df_nodes["budget_flow_area"] = [self.doc.budgetComponentsQueryFlowAtNode2(bdgt, n)[2] for n in
                                                map(int, df_nodes.index)]
                df_nodes["budget_flow_storage"] = [self.doc.budgetComponentsQueryFlowAtNode2(bdgt, n)[3] for n in
                                                   map(int, df_nodes.index)]
                self.doc.pdoc.budgetClose(bdgt)

            # compute nodal values for the mass budget
            if "mass" in budget:
                bdgt = self.doc.budgetMassCreate()
                df_nodes["budget_mass_bc"] = [self.doc.budgetComponentsQueryFlowAtNode2(bdgt, n)[1] for n in
                                              map(int, df_nodes.index)]
                df_nodes["budget_mass_area"] = [self.doc.budgetComponentsQueryFlowAtNode2(bdgt, n)[2] for n in
                                                map(int, df_nodes.index)]
                df_nodes["budget_mass_storage"] = [self.doc.budgetComponentsQueryFlowAtNode2(bdgt, n)[3] for n in
                                                   map(int, df_nodes.index)]
                self.doc.pdoc.budgetClose(bdgt)

            # compute nodal values for the heat heat budget
            if "heat" in budget:
                bdgt = self.doc.budgetHeatCreate()
                df_nodes["budget_heat_bc"] = [self.doc.budgetComponentsQueryFlowAtNode2(bdgt, n)[1] for n in
                                              map(int, df_nodes.index)]
                df_nodes["budget_heat_area"] = [self.doc.budgetComponentsQueryFlowAtNode2(bdgt, n)[2] for n in
                                                map(int, df_nodes.index)]
                df_nodes["budget_heat_storage"] = [self.doc.budgetComponentsQueryFlowAtNode2(bdgt, n)[3] for n in
                                                   map(int, df_nodes.index)]
                self.doc.pdoc.budgetClose(bdgt)

        return df_nodes.replace(-99999.0, np.nan)

    def faces(self, global_cos=True, selection=None):

        import pandas as pd

        # create a GeoDataFrame from the mesh
        df_faces = pd.DataFrame(index=range(self.doc.getNumberOfNodes()))
        df_faces.index.name = "FACE"

        # seems that these are the only API functions for faces
        #self.doc.queryFaceElements()
        #self.doc.queryFaceNodes()


    def edges(self, global_cos=True, selection=None):

        import pandas as pd

        # create a GeoDataFrame from the mesh
        df_edges = pd.DataFrame(index=range(self.doc.getNumberOfNodes()))
        df_edges.index.name = "EDGE"

        # seems that these are the only API functions for faces
        #self.doc.queryEdgeElements()
        #self.doc.queryEdgeNodes()


    def get_available_items(self, Type=None):
        """
        Return a list of available Parameters that can be obtained by calling doc.c.mesh.df.nodes or
        doc.c.mesh.df.elements, respectively.

        :param Type: Filter by Type ("elemental" or "nodal")
        :type Type: str

        :return: DataFrame with available items
        :rtype: pandas.DataFrame
        """
        # TODO: Generalize and move to Enum!

        import pandas as pd

        available_items = []
        for e in [e for e in dir(Enum) if "P_" in e]:
            e_num = eval("Enum." + e)
            try:
                ii = self.doc.getParamSize(e_num)
                if ii == self.doc.getNumberOfNodes() and ii == self.doc.getNumberOfElements():
                    itemtype = 'ambiguous'  # n_nodes = n_elements, can't determine type
                elif ii == self.doc.getNumberOfNodes():
                    itemtype = 'nodal'
                elif ii == self.doc.getNumberOfElements():
                    itemtype = 'elemental'
                else:
                    itemtype = 'unknowm'
                available_items.append((e, e_num, itemtype))
            except Exception:
                pass

        df_items = pd.DataFrame(available_items, columns=["Name", "Enum_Constant", "Type"])

        # filter by type
        if Type is not None:
            df_items = df_items[df_items.Type == Type]

        df_items.set_index("Enum_Constant", inplace=True)

        return df_items

    def mlw(self):
        """
        Return a pandas.DataFrame with information on all Multi-Layer wells in the model.

        :return: Dataframe with information on Mullti-Layer-wells
        :rtype: pandas.DataFrame
        """
        import pandas as pd
        data = self.doc.c.mesh.mlw()
        df = pd.DataFrame(data)
        df.set_index("mlw_id", inplace=True)
        return df

    def dfe(self):
        """
        Reutrn a DataFrame with information on Discrete Feature Elements in the model.

        :return: DataFrame with information on DFE
        :rtype: pandas.DataFrame
        """
        if self.doc.getNumberOfDimensions() != 3:
            raise NotImplementedError("this function is currently only available for 3D problems")

        import pandas as pd

        df_dfe = pd.DataFrame(
            [self.doc.getNodalArrayOfFractureElement(f) for f in range(self.doc.getNumberOfTotalFractureElements())],
            columns=["node_1", "node_2"])
        df_dfe.index.name = "dfe"

        df_dfe["law"] = [
            self.doc.getFracLaw(f, Enum.FRAC_1D, Enum.ALL_FRAC_MODES) for f in
            range(self.doc.getNumberOfTotalFractureElements())]

        df_dfe["area"] = [
            self.doc.getFracArea(f, Enum.FRAC_1D, Enum.ALL_FRAC_MODES, Enum.ALL_FRAC_LAWS) for f in
            range(self.doc.getNumberOfTotalFractureElements())]

        df_dfe["diameter"] = [
            self.doc.getFracElementDiameter(f) for f in
            range(self.doc.getNumberOfTotalFractureElements())]

        df_dfe["conductivity"] = [
            self.doc.getFracFlowConductivity(f, Enum.ALL_FRAC_TYPES, Enum.ALL_FRAC_MODES, Enum.ALL_FRAC_LAWS) for f in
            range(self.doc.getNumberOfTotalFractureElements())]

        df_dfe["storativity"] = [
            self.doc.getFracFlowStorativity(f, Enum.ALL_FRAC_TYPES, Enum.ALL_FRAC_MODES, Enum.ALL_FRAC_LAWS) for f in
            range(self.doc.getNumberOfTotalFractureElements())]

        # finalize
        return df_dfe
