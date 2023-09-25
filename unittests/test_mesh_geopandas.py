import unittest
import ifm_contrib as ifm
from ifm import Enum

class TestMeshGpd(unittest.TestCase):

    def test_elements(self):
        doc = ifm.loadDocument("./models/example_2D.fem")
        gdf = doc.c.mesh.gdf.elements([Enum.P_TRANS])
        self.assertAlmostEqual(gdf[Enum.P_TRANS].sum(), 741.2000004276633)
        doc.c.mesh.gdf.elements(par=Enum.P_TRANS)  # 0
        doc.c.mesh.gdf.elements(par=[Enum.P_TRANS])  # 0
        doc.c.mesh.gdf.elements(par={"Transmissivity": Enum.P_TRANS})  # 0
        doc.c.mesh.gdf.elements(par=[Enum.P_TRANS], expr="elemental_expr_test")
        doc.c.mesh.gdf.elements(par=[Enum.P_TRANS], expr=["elemental_expr_test"])
        doc.c.mesh.gdf.elements(par=[Enum.P_TRANS], expr=["elemental_expr_test"], distr="elemental_test")
        doc.c.mesh.gdf.elements(par=[Enum.P_TRANS], expr=["elemental_expr_test"], distr=["elemental_test"])
        doc.c.mesh.gdf.elements(par=[Enum.P_TRANS], layer=1)  # 0

        doc.c.mesh.gdf.elements(content=None)
        doc.c.mesh.gdf.elements(content=False)
        doc.c.mesh.gdf.elements(content=True)
        doc.c.mesh.gdf.elements(content=Enum.TOTAL_VOLUME)
        doc.c.mesh.gdf.elements(content=[Enum.TOTAL_VOLUME, Enum.VOID_VOLUME])

    def test_nodes(self):
        doc = ifm.loadDocument("./models/example_2D.fem")
        doc.c.mesh.gdf.nodes(par=Enum.P_HEAD)   # 0
        doc.c.mesh.gdf.nodes(par=[Enum.P_HEAD])  # 0
        doc.c.mesh.gdf.nodes(par={"Head": Enum.P_HEAD})  # 0
        doc.c.mesh.gdf.nodes(par=[Enum.P_HEAD], expr="nodal_expr_test")
        doc.c.mesh.gdf.nodes(par=[Enum.P_HEAD], expr=["nodal_expr_test"])
        doc.c.mesh.gdf.nodes(par=[Enum.P_HEAD], expr=["nodal_expr_test"], distr="nodal_test")
        doc.c.mesh.gdf.nodes(par=[Enum.P_HEAD], expr=["nodal_expr_test"], distr=["nodal_test"])
        doc.c.mesh.gdf.nodes(par=[Enum.P_HEAD], slice=1)  # 0
        # self.assertAlmostEqual(df[Enum.P_TRANS].sum(), 741.2000004276633)

        doc = ifm.loadDocument("./models/example_2D.dac")
        doc.pdoc.loadTimeStep(1)  # t=10.0 days
        doc.c.mesh.gdf.nodes(budget="flow")
        doc.c.mesh.gdf.nodes(budget=["flow"])
        doc.c.mesh.gdf.nodes(budget=True)
        df = doc.c.mesh.gdf.nodes(budget="flow")
        self.assertAlmostEqual(df.budget_flow_bc.sum(), -5.2016302997540258)
        self.assertAlmostEqual(df.budget_flow_area.sum(), 23.580393938311079)
        self.assertAlmostEqual(df.budget_flow_storage.sum(), -18.378763638890959)

    def test_mlw(self):
        doc = ifm.loadDocument("./models/example_3D_mspecies.fem")
        doc.c.mesh.gdf.mlw()


if __name__ == '__main__':
    unittest.main()
