import unittest
import ifm_contrib as ifm
from ifm import Enum

class TestMeshGpd(unittest.TestCase):

    def test_elements(self):
        ifm.forceLicense("Viewer")
        doc = ifm.loadDocument("./models/example_2D.fem")
        gdf = doc.c.mesh.gdf.elements([Enum.P_TRANS])
        self.assertAlmostEqual(gdf[Enum.P_TRANS].sum(), 741.2000004276633)
        doc.c.mesh.df.elements(par=Enum.P_TRANS)  # 0
        doc.c.mesh.df.elements(par=[Enum.P_TRANS])  # 0
        doc.c.mesh.df.elements(par={"Transmissivity": Enum.P_TRANS})  # 0
        doc.c.mesh.df.elements(par=[Enum.P_TRANS], expr="elemental_expr_test")
        doc.c.mesh.df.elements(par=[Enum.P_TRANS], expr=["elemental_expr_test"])
        doc.c.mesh.df.elements(par=[Enum.P_TRANS], expr=["elemental_expr_test"], distr="elemental_test")
        doc.c.mesh.df.elements(par=[Enum.P_TRANS], expr=["elemental_expr_test"], distr=["elemental_test"])
        doc.c.mesh.df.elements(par=[Enum.P_TRANS], layer=1)  # 0