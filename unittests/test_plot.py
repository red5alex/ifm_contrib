import unittest
import ifm_contrib as ifm
from ifm import Enum
import numpy as np
import geopandas as gpd
import pandas as pd

class TestPlot(unittest.TestCase):

    def test_faces(self):
        self.doc = ifm.loadDocument("./models/example_2D.dac")
        self.doc.c.plot.faces()

    def test_edges(self):
        self.doc = ifm.loadDocument("./models/example_2D.dac")
        self.doc.c.plot.edges()

    def test_continuous(self):
        self.doc = ifm.loadDocument("./models/example_2D.dac")
        self.doc.c.plot.continuous(par=Enum.P_HEAD)


    def test_patches(self):
        self.doc = ifm.loadDocument("./models/example_2D_unconf.fem")  # pure triangle mesh
        self.doc.c.plot._contours(par=Enum.P_COND, style="patches")
        self.doc.c.plot.patches(par=Enum.P_COND)

    def test_fringes(self):
        self.doc = ifm.loadDocument("./models/example_2D.dac")
        self.doc.c.plot.fringes(par=Enum.P_HEAD, alpha=1, cmap="feflow_blue_green_red")

    def test_isolines(self):
        self.doc = ifm.loadDocument("./models/example_2D.dac")
        self.doc.c.plot.isolines(par=Enum.P_HEAD, colors="black")

    def test_obs_markers(self):
        self.doc = ifm.loadDocument("./models/example_2D.dac")
        self.doc.c.plot.obs_markers()
        self.doc.c.plot.obs_markers(filter_by={"label": ["myObsPoint1", "myObsPoint2"]})

    def test_obs_labels(self):
        self.doc = ifm.loadDocument("./models/example_2D.dac")
        self.doc.c.plot.obs_labels()
        self.doc.c.plot.obs_labels(filter_by={"label": ["myObsPoint1", "myObsPoint2"]})


if __name__ == '__main__':
    unittest.main()
