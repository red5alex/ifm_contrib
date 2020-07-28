from ifm import Enum
import pandas as pd

class SettingsPd:
    """
    Functions for reading and writing global settings as pandas.DataFrames
    """

    def __init__(self, doc):
        self.doc = doc

    def species(self):
        """
        Return a table with information on available species
        :return: DataFrame with Species Information
        """

        df = pd.DataFrame()
        df["Name"] = [self.doc.getSpeciesName(s) for s in range(self.doc.getNumberOfSpecies())]
        df["Type"] = [self.doc.getSpeciesType(s) for s in range(self.doc.getNumberOfSpecies())]
        df["PhaseType"] = [self.doc.getSpeciesPhaseType(s) for s in range(self.doc.getNumberOfSpecies())]
        df["SpeciesKineticsType"] = [self.doc.getSpeciesKineticsType(s) for s in
                                             range(self.doc.getNumberOfSpecies())]
        df.index.name = "SpeciesID"
        return df

        # doc.getSpeciesKineticsArrhenius(0)
        # doc.getSpeciesKineticsMonod(0)
        # doc.getSpeciesKineticsUserDefined(0)