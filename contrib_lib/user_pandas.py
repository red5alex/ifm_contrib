from warnings import warn
# from ifm import Enum
import pandas as pd


class UserPd:
    """
    Functions regarding User Data (Distributions and Expressions)
    """

    def __init__(self, doc):
        self.doc = doc

    def info(self):
        warn("doc.c.user.df.info() is depreciated. Use doc.c.user.df.distributions()", FutureWarning)
        return self.distributions()

    def distributions(self):
        """
        Returns a pandas.DataFrame with information on existing user distributions.
        """

        # elemental Distribution
        if self.doc.pdoc.getNumberOfElementalRefDistr() > 0:
            df_dist_e = pd.DataFrame(
                [self.doc.getElementalRefDistrName(i) for i in range(self.doc.pdoc.getNumberOfElementalRefDistr())], 
                columns=["Name"])
            df_dist_e["user_type"] = "DISTRIBUTION"
            df_dist_e["item_type"] = "ELEMENTAL"
            df_dist_e.index.name = "ID"
            df_dist_e.reset_index(inplace=True)
        else:
            df_dist_e = pd.DataFrame(columns=["Name", "user_type", "item_type"])

        # nodal Distribution
        if self.doc.pdoc.getNumberOfNodalRefDistr() > 0:
            df_dist_n = pd.DataFrame(
                [self.doc.getNodalRefDistrName(i) for i in range(self.doc.pdoc.getNumberOfNodalRefDistr())], 
                columns=["Name"]) 
            df_dist_n.columns = ["Name"]
            df_dist_n["user_type"] = "DISTRIBUTION"
            df_dist_n["item_type"] = "NODAL"
            df_dist_n.index.name = "ID"
            df_dist_n.reset_index(inplace=True)
        else:
            df_dist_n = pd.DataFrame(columns=["Name", "user_type", "item_type"])

        # elemental Expression
        if self.doc.pdoc.getNumberOfElementalExprDistr() > 0:
            df_expr_e = pd.DataFrame(
                [self.doc.getElementalExprDistrName(i) for i in range(self.doc.pdoc.getNumberOfElementalExprDistr())],
                columns = ["Name"])
            df_expr_e["user_type"] = "EXPRESSION"
            df_expr_e["item_type"] = "ELEMENTAL"
            df_expr_e.index.name = "ID"
            df_expr_e.reset_index(inplace=True)
        else:
            df_expr_e = pd.DataFrame(columns=["Name", "user_type", "item_type"])

        # nodal Expression
        if self.doc.pdoc.getNumberOfNodalExprDistr() > 0:
            df_expr_n = pd.DataFrame(
                [self.doc.getNodalExprDistrName(i) for i in range(self.doc.pdoc.getNumberOfNodalExprDistr())],
                columns = ["Name"])
            df_expr_n["user_type"] = "EXPRESSION"
            df_expr_n["item_type"] = "NODAL"
            df_expr_n.index.name = "ID"
            df_expr_n.reset_index(inplace=True)
        else:
            df_expr_n = pd.DataFrame(columns=["Name", "user_type", "item_type"])

        # concatenate all lists 
        df = pd.concat([df_dist_e, df_dist_n, df_expr_e, df_expr_n])
        
        # concatenation may cause a cast to float - repair before return
        df["ID"] = df["ID"].astype(int)
        return df
