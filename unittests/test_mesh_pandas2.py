import unittest
import ifm_contrib as ifm
from ifm import Enum


class TestMeshPd(unittest.TestCase):

    def test_elements(self):
        doc = ifm.loadDocument("./models/example_2D.fem")
        df = doc.c.mesh.df.elements([Enum.P_TRANS])
        self.assertAlmostEqual(df[Enum.P_TRANS].sum(), 741.2000004276633)
        doc.c.mesh.df.elements(par=Enum.P_TRANS)   # 0
        doc.c.mesh.df.elements(par=[Enum.P_TRANS])  # 0
        doc.c.mesh.df.elements(par={"Transmissivity": Enum.P_TRANS})  # 0
        doc.c.mesh.df.elements(par=[Enum.P_TRANS], expr="elemental_expr_test")
        doc.c.mesh.df.elements(par=[Enum.P_TRANS], expr=["elemental_expr_test"])
        doc.c.mesh.df.elements(par=[Enum.P_TRANS], expr=["elemental_expr_test"], distr="elemental_test")
        doc.c.mesh.df.elements(par=[Enum.P_TRANS], expr=["elemental_expr_test"], distr=["elemental_test"])
        doc.c.mesh.df.elements(par=[Enum.P_TRANS], layer=1)  # 0

        doc.c.mesh.df.elements(content=None)
        doc.c.mesh.df.elements(content=False)
        doc.c.mesh.df.elements(content=True)
        doc.c.mesh.df.elements(content=Enum.TOTAL_VOLUME)
        doc.c.mesh.df.elements(content=[Enum.TOTAL_VOLUME, Enum.VOID_VOLUME])

        doc = ifm.loadDocument("./models/example_partial_unstruct.fem")
        
        # TODO: some of the next calls result in divide by zero error
        import numpy as np
        np.seterr(divide='ignore')
        
        df = doc.c.mesh.df.elements()

        doc = ifm.loadDocument("./models/example_fully_unstruct.fem")
        df = doc.c.mesh.df.elements()

        doc = ifm.loadDocument("./models/example_3D_mspecies.fem")
        doc.c.mesh.df.elements(aux="auxLayerThickness")
        doc.c.mesh.df.elements(aux=["auxLayerThickness"])
        doc.c.mesh.df.elements(aux={"layer_thickness": "auxLayerThickness"})



    def test_nodes(self):
        doc = ifm.loadDocument("./models/example_2D.fem")
        doc.c.mesh.df.nodes(par=Enum.P_HEAD)   # 0
        doc.c.mesh.df.nodes(par=[Enum.P_HEAD])  # 0
        doc.c.mesh.df.nodes(par={"Head": Enum.P_HEAD})  # 0
        doc.c.mesh.df.nodes(par=[Enum.P_HEAD], expr="nodal_expr_test")
        doc.c.mesh.df.nodes(par=[Enum.P_HEAD], expr=["nodal_expr_test"])
        doc.c.mesh.df.nodes(par=[Enum.P_HEAD], expr=["nodal_expr_test"], distr="nodal_test")
        doc.c.mesh.df.nodes(par=[Enum.P_HEAD], expr=["nodal_expr_test"], distr=["nodal_test"])
        doc.c.mesh.df.nodes(par=[Enum.P_HEAD], slice=1)  # 0
        # self.assertAlmostEqual(df[Enum.P_TRANS].sum(), 741.2000004276633)

        doc = ifm.loadDocument("./models/example_partial_unstruct.fem")
        df = doc.c.mesh.df.nodes()

        doc = ifm.loadDocument("./models/example_fully_unstruct.fem")
        df = doc.c.mesh.df.nodes()

        # test nodal budget option
        doc = ifm.loadDocument("./models/example_2D.dac")
        doc.pdoc.loadTimeStep(1)  # t=10.0 days
        doc.c.mesh.df.nodes(budget="flow")
        doc.c.mesh.df.nodes(budget=["flow"])
        doc.c.mesh.df.nodes(budget=True)
        df = doc.c.mesh.df.nodes(budget="flow")
        self.assertAlmostEqual(df.budget_flow_bc.sum() , -5.2016302997540258)
        self.assertAlmostEqual(df.budget_flow_area.sum(), 23.580393938311079)
        self.assertAlmostEqual(df.budget_flow_storage.sum(), -18.378763638890959)

        doc = ifm.loadDocument("./models/example_3D_mspecies.fem")
        doc.c.mesh.df.nodes(aux="auxSliceDistance")
        doc.c.mesh.df.nodes(aux=["auxSliceDistance"])
        doc.c.mesh.df.nodes(aux={"slice_distance": "auxSliceDistance"})

    def test_availableitems(self):
        doc = ifm.loadDocument("./models/example_2D.fem")
        doc.c.mesh.df.get_available_items()

    def test_mlw(self):
        doc = ifm.loadDocument("./models/example_3D_mspecies.fem")
        doc.c.mesh.df.mlw()


if __name__ == '__main__':
    unittest.main()
