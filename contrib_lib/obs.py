from ifm import Enum


class Obs:
    """
    Extension child-class for IFM contributor's Extensions.
    Use this class to add functionality relating to OBSERVATION POINTS.
    Note: Functionality relating to the Observation Time Series should be implemented in the
          .hist class of this project.
    """

    def __init__(self, doc):
        self.doc = doc

    # add custom methods here
