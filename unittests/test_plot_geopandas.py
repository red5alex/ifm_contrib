import unittest
import ifm_contrib as ifm
from ifm import Enum
import numpy as np

class TestPlot(unittest.TestCase):

    def test_fringes(self):
        ifm.forceLicense("Viewer")
        doc = ifm.loadDocument(r".\models\example_2D.dac")
        doc.loadTimeStep(doc.getNumberOfTimeSteps() - 1)
        gdf = doc.c.plot.gdf.fringes(Enum.P_HEAD, levels=range(11))

        # check if levels are correct:
        np.testing.assert_almost_equal(gdf.layer.values, [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5],
                                       err_msg="layer mismatch in geodataframe")
        np.testing.assert_almost_equal(gdf["400_min"].values,[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0],
                                       err_msg="min mismatch in geodataframe")
        np.testing.assert_almost_equal(gdf["400_max"].values,[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
                                       err_msg="max mismatch in geodataframe")

        # check if areas are equal:
        np.testing.assert_almost_equal(gdf.area.values,
                                        [13796.629903420493,
                                         17685.488005454623,
                                         57801.21973911512,
                                         208946.10078203367,
                                         127619.03879584387,
                                         168114.83724497937,
                                         46008.85589276335,
                                         42050.452606210514,
                                         33087.11588266799,
                                         26060.024132845527],
                                       err_msg="areas of polygon differs")
        doc.closeDocument()

        doc = ifm.loadDocument(r".\models\example_3D_mspecies.fem")
        gdf = doc.c.plot.gdf.fringes(Enum.P_HEAD)
        gdf = doc.c.plot.gdf.fringes(Enum.P_HEAD, levels=range(11))
        doc.closeDocument()

    def test_isolines(self):
        ifm.forceLicense("Viewer")
        doc = ifm.loadDocument(r".\models\example_2D.dac")
        doc.loadTimeStep(doc.getNumberOfTimeSteps() - 1)
        gdf = doc.c.plot.gdf.isolines(Enum.P_HEAD)
        gdf = doc.c.plot.gdf.isolines(Enum.P_HEAD, levels=range(11))
        #TODO: add tests for distributions and expressions
        doc.closeDocument()

        ifm.forceLicense("Viewer")
        doc = ifm.loadDocument(r".\models\example_3D_mspecies.fem")
        doc.loadTimeStep(doc.getNumberOfTimeSteps() - 1)
        gdf = doc.c.plot.gdf.isolines(par=Enum.P_HEAD, slice=1)
        gdf = doc.c.plot.gdf.isolines(par=Enum.P_HEAD, levels=range(11))
        #TODO: add tests for distributions and expressions

        doc.closeDocument()


