from ifm import Enum
from .settings_pandas import SettingsPd

class Settings:
    """
    Functions for reading and writing global settings
    """

    def __init__(self, doc):
        self.doc = doc

        # add custom child-classes here
        self.df = SettingsPd(doc)

    # add custom methods here
