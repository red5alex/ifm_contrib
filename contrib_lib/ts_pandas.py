# from ifm import Enum
import pandas as pd


class TsPd:

    def __init__(self, doc):
        self.doc = doc

    def info(self):
        """
        Returns a pandas.DataFrame with information on existing time series (formerly power functions).
        """

        list_info = self.doc.c.ts.info()
        df = pd.DataFrame(list_info, columns=["tsid", "comment", "no_point", "is_cyclic_num", "interpolation_kind"])
        df.set_index("tsid", inplace=True)
        df["is_cyclic"] = df.is_cyclic_num.astype(bool)
        del (df["is_cyclic_num"])
        return df

    def points(self, tsid, force_time_axis=False, reference_time=None):
        """
        Returns the values of a given time series (formerly power function) as a dataframe.

        :param tsid:             time series ID
        :type tsid:              int or convertible to int
        :param force_time_axis:  If True, the index of the dataframe will be the simulation time in days.
                                 If False (default), the index type will be of type datetime if a reference time is set
                                 in the model, and simulation time in days otherwise.
        :type force_time_axis:   bool
        :param reference_time:   Specify (or override) a reference time. Note that this only accounts for this export
                                 and is not a permanent change of the model settings.
        :type reference_time:    datetime.datetime

        :return:                 time series as a pandas.DataFrame
        :rtype:                  pandas.DataFrame
        """

        # make sure tsid is a valid number

        if type(tsid) == str:
            # if the tsid is called by its comment, we first need to check if the comment is a unique identifier
            # (not guaranteed by FEFLOW)
            df_info = self.doc.c.ts.df.info()
            # check if the comment can be found at all
            if len(df_info[df_info.comment == tsid]) < 1:
                raise KeyError("no time series with comment {} found!".format(tsid))
            # check if the choice is unique
            if len(df_info[df_info.comment == tsid]) > 1:
                raise RuntimeError("Multiple time series with comment {} found!".format(tsid))
            # OK!
            tsid = df_info[df_info.comment == tsid].index[0]

        try:
            tsid = int(tsid)
        except ValueError:
            raise ValueError("tsid must be of type int or convertible to type int")

        # test if time series exists
        if not self.doc.c.ts.exists(tsid):
            raise ValueError("Time Series {} does not exist.".format(tsid))

        # test if time series is empty, return empty dataframe if so
        if self.doc.powerGetNumberOfPoints(tsid) == 0:
            df = pd.DataFrame(columns=["Simulation Time", "Values"])
            df.set_index("Simulation Time", inplace=True)
            return df

        # get list of points and convert to DataFrame
        df = pd.DataFrame(self.doc.c.ts.points(tsid), columns=["Simulation Time", "Values"])
        df.set_index("Simulation Time", inplace=True)

        # convert time axis to datetime
        if self.doc.getReferenceTime() is None and reference_time is None:
            force_time_axis = True

        if reference_time is None:
            reference_time = self.doc.getReferenceTime()

        if force_time_axis:
            # we are done here, return df
            return df

        # convert time axis to datetime
        df["Simulation Time"] = pd.to_datetime(df.index, unit="D", origin=reference_time)
        df.set_index("Simulation Time", inplace=True)
        return df
