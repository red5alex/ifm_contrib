import os

from ifm import Enum

from .dfe import Dfe
from .diag import Diag
from .hist import Hist
from .mesh import Mesh
from .obs import Obs
from .plot import Plot
from .settings import  Settings
from .ts import Ts

class IfmContrib:
    """"
    Container Class for contributors extension classes.
    RESERVED FOR HIGH LEVEL FUNCTIONS, PLEASE DO NOT EDIT!
    PLEASE ADD CODE TO APPROPRIATE CHILD-CLASSES.
    """

    def __init__(self, doc):
        self.doc = doc

        # import child-classes
        # If adding additional childs and planning to contribute to the project,
        # please consult the maintainer of the repository about extending name space convention.
        self.dfe = Dfe(doc)
        self.diag = Diag(doc)
        self.hist = Hist(doc)
        self.mesh = Mesh(doc)
        self.obs = Obs(doc)
        self.plot = Plot(doc)
        self.settings = Settings(doc)
        self.ts = Ts(doc)

    def show_credits(self):
        for line in open(os.path.dirname(__file__)+"../../credits.md"):
            print(line.strip())

    def show_license(self):
        for line in open(os.path.dirname(__file__)+"../../LICENSE"):
            print(line.strip())

    def show_readme(self):
        for line in open(os.path.dirname(__file__) + "../../README.MD"):
            print(line.strip())
