import unittest
import ifm_contrib as ifm
from ifm import Enum
import numpy as np
import geopandas as gpd
import pandas as pd

class TestPlot(unittest.TestCase):

    def test_faces(self):
        self.doc = ifm.loadDocument(r".\models\example_2D.dac")
        self.doc.c.plot.faces()

    def test_edges(self):
        self.doc = ifm.loadDocument(r".\models\example_2D.dac")
        self.doc.c.plot.edges()

    def test_continuous(self):
        self.doc = ifm.loadDocument(r".\models\example_2D.dac")
        self.doc.c.plot.continuous(par=Enum.P_HEAD)

    def test_fringes(self):
        self.doc = ifm.loadDocument(r".\models\example_2D.dac")
        self.doc.c.plot.fringes(par=Enum.P_HEAD, alpha=1)

    def test_isolines(self):
        self.doc = ifm.loadDocument(r".\models\example_2D.dac")
        self.doc.c.plot.isolines(par=Enum.P_HEAD, colors="black")
