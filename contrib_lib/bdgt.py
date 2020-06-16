from ifm import Enum
import pandas as pd


# from .sdba_pandas import SdbaPd


class SubDomainBudget:

    def __init__(self, doc, domain, masking_domain, budget_type=Enum.PCLS_FLOW):

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
                        'NodalValue': self.sdb.getNodalValue(),
                        'TransferIn': self.sdb.getTransferIn(),
                        'TransferOut': self.sdb.getTransferOut(),
                        'WellIn': self.sdb.getWellIn(),
                        'WellOut': self.sdb.getWellOut()}

        self.nodal_flux = self.sdb_raw["NodalValue"]

        # create seperate objects for in out and net components
        self.sdb_in = {k[:-2]: self.sdb_raw[k] for k in self.sdb_raw if k.endswith("In")}
        self.sdb_out = {k[:-3]: self.sdb_raw[k] for k in self.sdb_raw if k.endswith("Out")}
        self.sdb_net = {k: self.sdb_in[k] - self.sdb_out[k] for k in self.sdb_in}

    def df_nodal_flux(self):
        df_q = pd.DataFrame(index=self.masking_domain)
        df_q["q"] = self.sdb.getNodalValue()
        df_q.dropna(subset=["q"], inplace=True)
        return df_q.join(self.doc.c.mesh.df.nodes())

    def gdf_nodal_flux(self):
        import geopandas as gpd
        return self.df_nodal_flux()[["q"]].join(self.doc.c.mesh.gdf.nodes()).set_geometry("element_shape")


class Bdgt:
    """
    Functions for working with selections.
    """

    def __init__(self, doc):
        self.doc = doc

        # add custom child-classes here
        # self.df = SdbaPd(doc)

    # add custom methods here

    def get_subdomainbudget(self, domain, masking_domain, budget_type=Enum.PCLS_FLOW):
        return SubDomainBudget(self.doc, domain, masking_domain, budget_type)
