from ifm import Enum

from .plot_geopandas import PlotGpd


class Plot:
    """
    Extension child-class for IFM contributor's Extensions.
    Use this class to add functionality relating to VISUALISATION routine of a FEFLOW model.
    """

    def __init__(self, doc):
        self.doc = doc

        # add custom child-classes here
        self.gdf = PlotGpd(doc)

    # add custom methods here