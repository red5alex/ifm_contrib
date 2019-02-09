import unittest
import ifm_contrib as ifm
# from ifm import Enum


class TestObsGpd(unittest.TestCase):

    def test_obspoints(self):
        ifm.forceLicense("Viewer")
        doc = ifm.loadDocument("./models/example_2D.fem")
        gdf = doc.c.obs.gdf.obspoints()
        self.assertEqual(3, len(gdf))  # should return three observation points
