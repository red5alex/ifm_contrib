from ifm import Enum

class ContentPd:
    """
    Functions for exporting nodal and elemental properties to GeoDataFrames.
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

    def content(self):
        """
        Get the model domains content (all content items).

        :return: DataFrame with all contents
        :rtype: pandas.DataFrame
        """
        import numpy as np

        df_content = self.doc.c.content.df.info()
        df_content["content"] = 0.
        for i in df_content.index:
            print(i)
            for e in range(self.doc.getNumberOfElements()):
                try:
                    df_content.loc[i, "content"] += self.doc.getElementalContent(i, e)
                except StandardError as e:
                    df_content.loc[i, "content"] = np.nan
                    break

        return df_content