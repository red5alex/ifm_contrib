import unittest
import ifm_contrib as ifm
from ifm import Enum
import numpy as np
import geopandas as gpd
import pandas as pd

class TestPlot(unittest.TestCase):

    def test_faces(self):
        ifm.forceLicense("Viewer")
        self.doc = ifm.loadDocument(r".\models\example_2D.dac")
        self.doc.c.plot.faces()

    def test_edges(self):
        ifm.forceLicense("Viewer")
        self.doc = ifm.loadDocument(r".\models\example_2D.dac")
        self.doc.c.plot.edges()

    def test_continuous(self):
        ifm.forceLicense("Viewer")
        self.doc = ifm.loadDocument(r".\models\example_2D.dac")
        self.doc.c.plot.continuous(par=Enum.P_HEAD)

    def test_fringes(self):
        ifm.forceLicense("Viewer")
        self.doc = ifm.loadDocument(r".\models\example_2D.dac")
        self.doc.c.plot.fringes(par=Enum.P_HEAD, alpha=1, cmap="feflow_blue_green_red")

    def test_isolines(self):
        ifm.forceLicense("Viewer")
        self.doc = ifm.loadDocument(r".\models\example_2D.dac")
        self.doc.c.plot.isolines(par=Enum.P_HEAD, colors="black")

    def test_obs_markers(self):
        ifm.forceLicense("Viewer")
        self.doc = ifm.loadDocument(r".\models\example_2D.dac")
        self.doc.c.plot.obs_markers()
        self.doc.c.plot.obs_markers(filter_by={"label": ["myObsPoint1", "myObsPoint2"]})

    def test_obs_labels(self):
        ifm.forceLicense("Viewer")
        self.doc = ifm.loadDocument(r".\models\example_2D.dac")
        self.doc.c.plot.obs_labels()
        self.doc.c.plot.obs_labels(filter_by={"label": ["myObsPoint1", "myObsPoint2"]})