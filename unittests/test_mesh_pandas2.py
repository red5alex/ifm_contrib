import unittest
import ifm_contrib as ifm
from ifm import Enum

class TestMeshGpd(unittest.TestCase):

    def test_elements(self):
        doc = ifm.loadDocument("./models/example_2D.fem")
        df = doc.c.mesh.df.elements([Enum.P_TRANS])
        self.assertAlmostEqual(df[Enum.P_TRANS].sum(), 741.2000004276633)