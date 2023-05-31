from ifm import Enum
import pandas as pd

from .bdgt_pandas import BdgtPd


class SubDomainBudgetTransferContrib:
    """
    Functions regarding information of the Budget Panels.
    """

    def __init__(self, doc, domain, masking_domain, budget_type=Enum.PCLS_FLOW):
        """

        :param doc:  the ifm_handler
        :param domain: Domain of Interest DOI. Can be either a list or set of element numbers, or the name of the selection
        :type domain: str, [int] or set(int)
        :param masking_domain:  Masking domain MD. Can be either a list or set of element numbers, or the name of the selection
        :type masking_domain: str, [int] or set(int)
        :param budget_type: one of ifm.Enum.PCLS_*
        """

        self.doc = doc

        self.budget_type = budget_type

        # parameter handling doi
        if type(domain) == str:
            self.domain = doc.c.sel.list(domain)
        elif type(domain) == set:
            self.domain = list(domain)
        elif type(domain) == list:
            self.domain = domain
        else:
            raise TypeError("domain must be of type list, set, or str")

        # parameter handling md
        if type(masking_domain) == str:
            self.masking_domain = doc.c.sel.convert(masking_domain, Enum.SEL_NODAL)
            # intersect = list(set(self.domain) & set(self.masking_domain))
            # self.masking_domain = intersect

        elif type(masking_domain) == set:
            self.masking_domain = list(masking_domain)
        elif type(masking_domain) == list:
            self.masking_domain = masking_domain
        else:
            raise TypeError("masking_domain must be of type list, set, or str")

        # compute budget
        try:
            self.sdb = self.doc.budgetComputeSubdomainTransfer(self.budget_type, self.domain, self.masking_domain, True)

        except RuntimeError as e:
            raise RuntimeError("FEFLOW has risen an error when computing the budget - is the simulator running?")

        # post-process budget for better readability - raw data
        self.sdb_raw = {'BorderIn': self.sdb.getBorderIn(),
                        'BorderOut': self.sdb.getBorderOut(),
                        'CauchyIn': self.sdb.getCauchyIn(),
                        'CauchyOut': self.sdb.getCauchyOut(),
                        'ConvIn': self.sdb.getConvIn(),
                        'ConvOut': self.sdb.getConvOut(),
                        'DirichletIn': self.sdb.getDirichletIn(),
                        'DirichletOut': self.sdb.getDirichletOut(),
                        'InternalDFIn': self.sdb.getInternalDFIn(),
                        'InternalDFOut': self.sdb.getInternalDFOut(),
                        'InternalPMIn': self.sdb.getInternalPMIn(),
                        'InternalPMOut': self.sdb.getInternalPMOut(),
                        'NeumannIn': self.sdb.getNeumannIn(),
                        'NeumannOut': self.sdb.getNeumannOut(),
                        'NodalValue': self.sdb.getNodalValues(),
                        'TransferIn': self.sdb.getTransferIn(),
                        'TransferOut': self.sdb.getTransferOut(),
                        'WellIn': self.sdb.getWellIn(),
                        'WellOut': self.sdb.getWellOut()}

        self.nodal_flux = self.sdb_raw["NodalValue"]

        # create seperate objects for in out and net components
        self.sdb_out = {k[:-3]: self.sdb_raw[k] for k in self.sdb_raw if k.endswith("Out")}
        self.sdb_in = {k[:-2]: self.sdb_raw[k] for k in self.sdb_raw if k.endswith("In")}
        self.sdb_net = {k: self.sdb_in[k] - self.sdb_out[k] for k in self.sdb_in}

    def df_nodal_flux(self):
        """
        Return Nodal Fluxes as a DataFrame.
        :return:
        """
        df_q = pd.DataFrame(index=self.masking_domain)
        df_q["q"] = self.sdb.getNodalValues()
        df_q.dropna(subset=["q"], inplace=True)
        return df_q.join(self.doc.c.mesh.df.nodes())

    def gdf_nodal_flux(self):
        """
        Return Nodal Fluxes as a GeoDataFrame.
        :return:
        """
        import geopandas as gpd
        return self.df_nodal_flux()[["q"]].join(self.doc.c.mesh.gdf.nodes()).set_geometry("element_shape")

    def df_sdb(self):
        """
        Returns a DataFrame with all components of the TransferBudget.
        :return:
        """
        df = pd.DataFrame(index=self.sdb_net.keys())
        df["out"] = [-q for q in self.sdb_out.values()]  # assign negative values
        df["in"] = self.sdb_in.values()
        df["net"] = self.sdb_net.values()
        return df

    def df_internal(self, doi, mds, corner_node_strategy="equal"):

        # parameter handling
        if corner_node_strategy != "equal":
            raise ValueError('"equal" is currently the only supported corner node strategy')

        # create temporary selection for all elements not in doi or mds
        element_other = set(range(self.doc.getNumberOfElements())) - self.doc.c.sel.set(doi)
        for md in mds:
            element_other -= self.doc.c.sel.set(md)
        if len(element_other) > 0:
            self.doc.c.sel.create(Enum.SEL_ELEMENTAL, "__other__", element_other)
            mds.append("__other__")

        # convert element selections to node selection, and intersect md with doi
        nodes_doi = self.doc.c.sel.convert(doi, Enum.SEL_NODAL)
        nodes_mds = {
            s: set(self.doc.c.sel.convert(s, Enum.SEL_NODAL)) & set(self.doc.c.sel.convert(doi, Enum.SEL_NODAL))
            for s in mds}

        # get budget, masked by itself
        sdba = self.doc.c.bdgt.get_subdomainbudgettransfer(doi, doi)

        # get nodal fluxes (border)
        df_q = sdba.df_nodal_flux()

        # add membership flag: is node member of MD? (one column per MD)
        for s in mds:
            df_q[s] = df_q.index.isin(nodes_mds[s])

        # count memberships
        df_q["n_memberships"] = df_q[mds].T.sum()

        # calculate nodal contribution to each md: total_flux div by memberships
        for s in mds:
            df_q["q_{}".format(s)] = 0.
            df_q.loc[df_q[s], "q_{}".format(s)] = df_q.q / df_q.n_memberships

        # delete temporary selection for other nodes
        self.doc.c.sel.delete("__other__")

        # create dataframe with fluxes
        df_result = pd.DataFrame(df_q[["q_{}".format(s) for s in mds]].sum(), columns=["net"])
        df_result.index = [s[2:] for s in df_result.index]
        return df_result


class Bdgt:
    """
    Functions for working with selections.
    """

    def __init__(self, doc):
        self.doc = doc

        # add custom child-classes here
        # self.df = SdbaPd(doc)

        # add custom child-classes here
        self.df = BdgtPd(doc)

    # add custom methods here

    def get_subdomainbudgettransfer(self, domain, masking_domain, budget_type=Enum.PCLS_FLOW):
        return SubDomainBudgetTransferContrib(self.doc, domain, masking_domain, budget_type)
