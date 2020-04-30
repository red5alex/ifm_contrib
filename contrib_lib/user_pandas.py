# from ifm import Enum
import pandas as pd


class UserPd:

    def __init__(self, doc):
        self.doc = doc

    def info(self):
        """
        Returns a pandas.DataFrame with information on existing user distributions.
        """

        # elemental Distribution
        df_dist_e = pd.DataFrame(
            [self.doc.getElementalRefDistrName(i) for i in range(self.doc.pdoc.getNumberOfElementalRefDistr())])
        df_dist_e.columns = ["Name"]
        df_dist_e["user_type"] = "DISTRIBUTION"
        df_dist_e["item_type"] = "ELEMENTAL"
        df_dist_e.index.name = "ID"
        df_dist_e.reset_index(inplace=True)

        # elemental Distribution
        df_dist_n = pd.DataFrame(
            [self.doc.getNodalRefDistrName(i) for i in range(self.doc.pdoc.getNumberOfNodalRefDistr())])
        df_dist_n.columns = ["Name"]
        df_dist_n["user_type"] = "DISTRIBUTION"
        df_dist_n["item_type"] = "NODAL"
        df_dist_n.index.name = "ID"
        df_dist_n.reset_index(inplace=True)

        # TODO: Does not work yet!

        # elemental Expression
        if self.doc.pdoc.getNumberOfElementalExprDistr() > 0:
            df_expr_e = pd.DataFrame(
                [self.doc.getElementalExprDistrName(i) for i in range(self.doc.pdoc.getNumberOfElementalExprDistr())])
            df_expr_e.columns = ["Name"]
            df_expr_e["user_type"] = "EXPRESSION"
            df_expr_e["item_type"] = "ELEMENTAL"
            df_expr_e.index.name = "ID"
            df_expr_e.reset_index(inplace=True)
        else:
            df_expr_e = pd.DataFrame(columns=["Name", "user_type", "item_type"])

        # nodal Expression
        df_expr_n = pd.DataFrame(
            [self.doc.getNodalExprDistrName(i) for i in range(self.doc.pdoc.getNumberOfNodalExprDistr())])
        df_expr_n.columns = ["Name"]
        df_expr_n["user_type"] = "EXPRESSION"
        df_expr_n["item_type"] = "NODAL"
        df_expr_n.index.name = "ID"
        df_expr_n.reset_index(inplace=True)

        return pd.concat([df_dist_e, df_dist_n, df_expr_e, df_expr_n])