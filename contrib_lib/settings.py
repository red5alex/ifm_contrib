from ifm import Enum


class Settings:
    """
    Extension child-class for IFM contributor's Extensions.
    Use this class to add functionality relating to PROBLEM SETTINGS.
    Note: Functionality relating diagnosing problems in the model should be implented in the
          .diag class of this project.
    """

    def __init__(self, doc):
        self.doc = doc

    # add custom methods here
