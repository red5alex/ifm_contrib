import unittest
import ifm_contrib as ifm
from ifm import Enum
import numpy as np
import geopandas as gpd
import pandas as pd

class TestPlot(unittest.TestCase):

    def test_mesh(self):
        self.doc = ifm.loadDocument(r".\models\example_2D.dac")
        self.doc.c.plot.mesh()

    def test_continuous(self):
        self.doc = ifm.loadDocument(r".\models\example_2D.dac")
        self.doc.c.plot.continuous(Enum.P_HEAD)

    def test_fringes(self):
        self.doc = ifm.loadDocument(r".\models\example_2D.dac")
        self.doc.c.plot.fringes(Enum.P_HEAD, alpha=1)

    def test_isolines(self):
        self.doc = ifm.loadDocument(r".\models\example_2D.dac")
        self.doc.c.plot.isolines(Enum.P_HEAD, colors="black")
