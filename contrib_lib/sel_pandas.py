from ifm import Enum


class SelPd:
    """
    Functions for getting informations on Selections in Pandas
    """

    def __init__(self, doc):
        self.doc = doc

    def selections(self, seltype=None):
        """
        Returns a DataFrame with information on selections of the selected type.
        :param seltype: One of ifm.Enum.SEL_*
        :return: DataFrame with information on selections
        :rtype: pandas.DataFrame
        """

        import pandas as pd

        # check parameters
        supported_types = [Enum.SEL_NODES,
                            Enum.SEL_ELEMS,
                            Enum.SEL_EDGES,
                            Enum.SEL_FRACS]
        if seltype is None:
            seltypes = supported_types
        elif seltype in supported_types:
            seltypes = [seltype]
        elif type(seltype) is list and any([s in supported_types for s in seltype ]):
            seltypes = seltype
        else:
            raise ValueError("bad seltype argument")

        df_all = pd.DataFrame()
        df_all.index.name = "selection_name"

        friendlynames = {Enum.SEL_NODES: "nodes",
                        Enum.SEL_ELEMS: "elements",
                        Enum.SEL_EDGES: "edges",
                        # (ifm.Enum.SEL_FACES, "faces"),
                        Enum.SEL_FRACS: "fractures"}

        for seltype in seltypes:
            df = pd.DataFrame(self.doc.c.sel.selections(seltype), columns=["selection_name"])
            df["SEL_TYPE"] = friendlynames[seltype]
            df["SEL_ENUM"] = seltype
            df["SEL_ID"] = df.index
            df["N_ITEMS"] = [self.doc.getSelectionItemCount(seltype, i) for i, row in df.iterrows()]
            df.set_index("selection_name", inplace=True)
            df_all = pd.concat([df_all, df])

        return df_all
