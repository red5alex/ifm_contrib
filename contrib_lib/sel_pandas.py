from ifm import Enum


class SelPd:
    """
    Functions for getting informations on Selections in Pandas
    """

    def __init__(self, doc):
        self.doc = doc

    def selections(self, seltype):
        """
        Returns a DataFrame with information on selections of the selected type.
        :param seltype: One of ifm.Enum.SEL_*
        :return: DataFrame with information on selections
        :rtype: pandas.DataFrame
        """

        import pandas as pd

        df = pd.DataFrame(self.doc.c.sel.getSelectionNames(seltype))
        df.columns = ["NAME"]
        df.index.name = "SEL_ID"

        # add selection type (const integert)
        df["SELTYPE"] = seltype

        # add number of items
        df["N_ITEMS"] = [self.doc.getSelectionItemCount(row.SELTYPE, i) for i, row in df.iterrows()]

        return df
