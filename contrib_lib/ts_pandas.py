import ifm
import pandas as pd
from warnings import warn

class TsPd:
    """
    Functions regarding time series (aka power functions)
    """

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

    def points(self, tsid=None, force_time_axis=False, reference_time=None):
        """
        Returns the values of a given time series (formerly power function) as a dataframe. Time Series can be
        identified by id or comment (will raise Warning if comment is not unique). Returns a DataFrame with multiple
        timeseries if tsid is provided as a list (will have nan-values if indices do not match).

        :param tsid:             time series ID or list of time series IDs, or None (default, return all)
        :type tsid:              int, or str, or [int or str]
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

        # if tsid not specified, return all by comment
        if tsid is None:
            tsid = list(self.doc.c.ts.df.info().comment)

        # if tsid is a list, return a dataframe with multiple columns by recursive call.
        if type(tsid) == list:
            df = pd.DataFrame()
            for ts in tsid:
                df[ts] = self.doc.c.ts.df.points(ts).Values
            return df

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
                raise RuntimeWarning("Multiple time series with comment {} found!".format(tsid))
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

    def create_from_series(self, tsid, series, comment=None, cyclic=False, interpolation=ifm.Enum.INTERPOL_LINEAR,
                           warn_on_overwrite=True, error_on_overwrite=False):
        """
        Create a FEFLOW time series from a pandas.Series.

        :param tsid: time series id
        :param series: pd.Series. index will be
        :param comment: comment to be set
        :param cyclic: True of cyclic (default: False)
        :param interpolation: Interpolation kind (default: ifm.Enum.INTERPOL_LINEAR)
        :param warn_on_overwrite: warn if ts id is occupied (default: True)
        :param error_on_overwrite: raise error if ts id is occupied (default: False)
        :return:
        """

        if comment is None:
            comment = "timeseries_{}".format(tsid)

        # create time series,
        if self.doc.c.ts.exists(tsid):
            if error_on_overwrite:
                raise RuntimeError("time series {} does already exist!".format(tsid))
            if warn_on_overwrite:
                warn(RuntimeWarning("time series {} does already exist!".format(tsid)))
            self.doc.c.ts.clear(tsid)
        else:
            self.doc.pdoc.powerCreateCurve(tsid)

        # convert to time axis is DateTimeIndex
        if type(series.index) == pd.DatetimeIndex:
            if self.doc.getReferenceTime() is None:
                raise RuntimeError("No ReferenceTime defined in FEFLOW, cannot convert DatetimeIndex")
            series.index = (series.index - self.doc.getReferenceTime()).days

        # add all points
        for time, value in zip(series.index, series.values):
            self.doc.powerSetPoint(tsid, time, value)

        # set metadata
        self.doc.powerSetComment(tsid, comment)
        self.doc.powerSetCyclic(tsid, cyclic)
        self.doc.powerSetInterpolationKind(tsid, interpolation)
