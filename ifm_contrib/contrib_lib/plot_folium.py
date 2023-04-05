from ifm import Enum


class PlotFolium:
    """
    Functions for exporting plotted data like isocontours as GeoDataFrame. Results are similar to the
    output of the View Components Panel of the FEFLOW GUI.
    """

    def __init__(self, doc):
        self.doc = doc
