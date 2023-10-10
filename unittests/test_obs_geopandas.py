import unittest
import ifm_contrib as ifm
# from ifm import Enum


class TestObsGpd(unittest.TestCase):

    def test_obspoints(self):
        doc = ifm.loadDocument("./models/example_2D.fem")

        # should return three observation points
        self.assertEqual(3, len(doc.c.obs.gdf.obspoints()))

        # should return two observation points
        self.assertEqual(2, len(doc.c.obs.gdf.obspoints(filter_by={"label": ["myObsPoint1", "myObsPoint2"]})))


if __name__ == '__main__':
    unittest.main()
