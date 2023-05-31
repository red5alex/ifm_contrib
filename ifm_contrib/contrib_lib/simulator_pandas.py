from ifm import Enum

from datetime import timedelta


class SimPd:
    """
    Functions regarding the simulator and data specific to results files, using Pandas
    """

    def __init__(self, doc):
        self.doc = doc

    def time_steps(self):
        """
        Get a DataFrame with information on timesteps saved in the dacfile.
        :return: DataFrame
        """

        import pandas as pd
        import numpy as np

        # get time step list and format as dataframe
        df = pd.DataFrame(self.doc.getTimeSteps())
        df.columns = ["step_index", "simulation_time", "timestep_length"]

        # add calendar column
        if self.doc.getReferenceTime() is not None:
            df["simulation_date"] = [self.doc.getReferenceTime() + timedelta(days=simtime) for simtime in
                                     df.simulation_time]
        else:
            df["simulation_date"] = np.nan

        # add file index
        df.index.name = "file_index"
        df.reset_index(inplace=True)

        # reorder columns
        df = df[['file_index', 'step_index', 'simulation_time', 'simulation_date', 'timestep_length']]

        return df.set_index("file_index")
