import unittest
import ifm_contrib as ifm
from ifm import Enum


class TestMeshGpd(unittest.TestCase):

    def test_elements(self):
        doc = ifm.loadDocument("./models/example_2D.fem")
        df = doc.c.mesh.df.elements([Enum.P_TRANS])
        self.assertAlmostEqual(df[Enum.P_TRANS].sum(), 741.2000004276633)

    def test_nodes(self):
        doc = ifm.loadDocument("./models/example_2D.fem")
        doc.c.mesh.df.nodes(par=Enum.P_HEAD)   # 0
        doc.c.mesh.df.nodes(par=[Enum.P_HEAD])  # 0
        doc.c.mesh.df.nodes(par={"Head": Enum.P_HEAD})  # 0
        doc.c.mesh.df.nodes(par=[Enum.P_HEAD], expr="nodal_expr_test")
        doc.c.mesh.df.nodes(par=[Enum.P_HEAD], expr=["nodal_expr_test"])
        doc.c.mesh.df.nodes(par=[Enum.P_HEAD], expr=["nodal_expr_test"], distr="nodal_test")
        doc.c.mesh.df.nodes(par=[Enum.P_HEAD], expr=["nodal_expr_test"], distr=["nodal_test"])
        # self.assertAlmostEqual(df[Enum.P_TRANS].sum(), 741.2000004276633)
