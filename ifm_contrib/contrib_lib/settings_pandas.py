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

    def lookup_table(self, names_as_index=True, readable_headers=False):
        """
        Return the models parameter lookup table as a DataFrame. 

        :param names_as_index: Use material names as index (default), otherwise use material ID.
        :param: readable_headers: Use human readable abbreviations instead of numeric parameter ids as headers. These correspond 
        to the name of the property in the ifm.Enum object, ommitting the leading `P_` (`ifm.Enum.P_CONDX` -> `CONDX`).
        :return: Parameter Lookup Table
        :rtype: pandas.DataFrame
        """

        # Version check
        import ifm
        if ifm.getKernelVersion() < 7458:
            raise RuntimeError("This function requires FEFLOW Version 7.5 or higher")

        # get lookup table
        lookuptable = self.doc.getLookupTable()

        # get materials
        df_lookuptable = pd.DataFrame(index=lookuptable.getMaterials().values())
        df_lookuptable.index.name = "material_id"
        df_lookuptable["material_name"] = [i for i in lookuptable.getMaterials()]

        # get properties
        df_properties = pd.DataFrame([lookuptable.getProperties(m) for m in lookuptable.getMaterials().values()])
        df_properties.index = lookuptable.getMaterials().values()

        # combine and format
        df_lookuptable = df_lookuptable.join(df_properties)
        if names_as_index is True:
            df_lookuptable = df_lookuptable.reset_index().set_index("material_name")

        # rename column headers from parameter ids to readable names
        if readable_headers:
            dict_ids = {getattr(ifm.Enum, c): c.replace("P_","") for c in dir(ifm.Enum) if c.startswith("P_")}
            df_lookuptable.columns = list(df_lookuptable.columns[:1]) + [dict_ids[c] for c in df_lookuptable.columns[1:]]
            
        return df_lookuptable