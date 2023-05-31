from ifm import Enum


class Diag:
    """
    Class for methods relating to diagnostic tests on the model.
    """

    def __init__(self, doc):
        self.doc = doc

    # add custom methods here

    def test_InOutTransferRate(self):

        # explanation
        info = {"warning_message" : "Differing In-/Out Transfer Rates found in steady-state model.",
                "level" :           "Warning",
                "explanation_str" : """If different In- and Out- Transfer Rates are used in a steady-state model, 
                                        FEFLOW does not consider changes between in- and outflow during the iteration 
                                        process. The steady-state solution may consequently alternate between two 
                                        states when repeatatively running the model.""",
                "relevant_for" :    "steady-state flow models"}

        # check if test is appropriate for this model
        if not self.doc.getTimeClass() in [Enum.TCLS_ST_UNST, Enum.TCLS_STEADY]:
            return None, info  #  n/a

        # do the test: does In/OutTransfer rates differ by more than 1% in any element?
        df_elements = self.doc.c.mesh.elements([Enum.P_TRAFIN, Enum.P_TRAFOUT])
        diff = df_elements[Enum.P_TRAFIN] / df_elements[Enum.P_TRAFOUT]
        if diff.min < 0.99 or diff.max > 1.01:
            return True, info  # failed
        else:
            return False, info # passed

"""
Tests to implement:
- check for non-zero Y-Offset in 2D vertical model


"""





