from ifm import Enum


class HistPd:

    def __init__(self, doc):
        self.doc = doc

    def __getattr__(self, item):
        # TODO: create dataframe as attribute, or raise Attribute Error
        if item in [i.replace("HIST_","") for i in dir(Enum) if "HIST" in i]:
            return self.getDataframe(item)
        else:
            raise AttributeError()

    def getDataframe(self, hist_type=None, hist_subtype=0, force_time_axis=False, reference_time=None):
        """
        returns the chosen history id as a DataFrame. Calling the function without arguments returns a dictionary of
        all available histories
        hist_type:    History Type (str, int, ifm.Enum.HIST_* constant or None.
        hist_subtype: History Sub-Type (int)
        force_time_axis: index uses FEFLOW time in days
        reference_time: specify reference_time (default: as set in FEFLOW)
        """

        hist_str = None

        import pandas as pd
        hist_defined = [c for c in dir(Enum) if c.startswith("HIST_")]

        if hist_type is None:
            all_hist = {}
            for hist in hist_defined:
                try:
                    result = self.getHistory(hist)
                    all_hist[hist] = result
                except TypeError:
                    pass

            return all_hist

        if type(hist_type) == str:
            if "HIST_" not in hist_type:
                hist_str = hist_type
                hist_type = "HIST_" + hist_type
            if hist_type not in hist_defined:
                msg = "Unknown History Type {}.".format(hist_type)
                msg += "available constants in ifm.Enum: "
                msg += ",".join(hist_defined)
                raise ValueError(msg)

            hist_type = Enum.__dict__[hist_type]

        chart = self.doc.getHistoryValues(hist_type, hist_subtype)

        times = chart[0]
        values = chart[1]
        itemnames = chart[2]

        df = pd.DataFrame(values, columns=times, index=itemnames, ).T
        df.index.name = "Simulation Time"

        # no further processing of reference time is not set or not applicable, or
        # force_time flag is set:
        if hist_type in ['ANA', 'MULTW_FLUX', 'BHE', 'VARIO']:
            force_time_axis = True
        if self.doc.getReferenceTime() is None and reference_time is None:
            force_time_axis = True
        if force_time_axis:
            self.__dict__[hist_type] = df
            if hist_str is not None:  # add the df permanently to class instance
                setattr(self, hist_str, df)
            return df

        # convert time axis to datetime
        if reference_time is None:
            reference_time = self.doc.getReferenceTime()
        df["Time"] = pd.to_datetime(df.index, unit="D", origin=reference_time)
        df.set_index("Time", inplace=True)

        if hist_str is not None:
            setattr(self, hist_str, df) # add the df permanently to class instance
        return df
