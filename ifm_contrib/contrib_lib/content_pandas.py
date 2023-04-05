from ifm import Enum

class ContentPd:
    """
    Functions regarding accessing information from the Content Panel as pandas.DataFrames.
    """

    def __init__(self, doc):
        self.doc = doc

    def info(self):
        """
        Return infomation on available content items.

        :return:  information on content items
        :rtype:   pandas.DataFrame
        """
        import pandas as pd
        features = [[Enum.TOTAL_VOLUME, 'TOTAL_VOLUME', 'Total volume', u"m3"],
                     [Enum.VOID_VOLUME, 'VOID_VOLUME', 'Void volume', u"m3"],
                     [Enum.FLUID_CONTENT, 'FLUID_CONTENT', 'Fluid content', u"m3"],
                     [Enum.DILUTED_MASS, 'DILUTED_MASS', 'Diluted mass (fluid phase)', u"g"],
                     [Enum.SORBED_MASS, 'SORBED_MASS', 'Sorbed mass (solid phase)', u"g"],
                     [Enum.ENERGY_FLUID, 'ENERGY_FLUID', 'Energy of fluid phase', u"J"],
                     [Enum.ENERGY_SOLID, 'ENERGY_SOLID', 'Energy of solid phase',u"J"],
                     [Enum.ENERGY_TOTAL, 'ENERGY_TOTAL', 'Total energy content',u"J"]
                   ]
        df_info = pd.DataFrame(features)
        df_info.columns = ["id", "ifm.Enum", "description", "unit"]
        return df_info.set_index("id")


    def content(self, model_domain=True, selection=None, content_types=True):
        """
        Get the model domains content (all content items).

        :return: DataFrame with all contents
        :rtype: pandas.DataFrame
        """

        # if single selection, make list with single entry
        if type(selection) != list:
            selection = [selection]

        # raise error if selection list entries are invalid
        for s in selection:
            if s is not None:
                if type(s) != str:
                    raise ValueError("selection must be None or str, or a list containing str and/or None members")
                if self.doc.findSelection == -1:
                    raise ValueError("No elemental selection '{}' found.".format(s))

        # get content by element
        df_elemental_content = self.doc.c.sel.df.elemental_content(content_types)

        for content_type in content_types:
            for sel in selection:
                if sel is None:
                    content = df_elemental_content[content_type].sum()
                else:
                    content = df_elemental_content.loc[self.doc.c.sel.list(sel)].TOTAL_VOLUME.sum()

        # TODO: the 'selection' parameter shall have this behavior:
        #       None - do nothing
        #       str - calculate the content of the elemental selection with this name
        #       [str, str] - calculate the content for multiple selections with this these names

        import numpy as np

        df_content = self.doc.c.content.df.info()
        df_content["content"] = 0.
        for i in df_content.index:
            for e in range(self.doc.getNumberOfElements()):
                try:
                    df_content.loc[i, "Model Domain"] += self.doc.getElementalContent(i, e)
                except StandardError as e:
                    df_content.loc[i, "Model Domain"] = np.nan
                    break

        return df_content