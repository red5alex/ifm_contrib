from ifm import Enum
from .simulator_pandas import SimPd

import sys
import os

from datetime import datetime, timedelta
from glob import glob
import pandas as pd
import matplotlib.pyplot as plt

class Simulator:
    """
    Functions regarding the simulator and data specific to results files
    """

    def __init__(self, doc):
        self.doc = doc

        # add custom child-classes here
        self.df = SimPd(doc)

    def suggest_dac_filename(self, relative=False):
        """
        Suggest a default file name for a results (dac) file.
        If the file is in a '/femdata' folder, will suggest the respective '/results' folder.
        Otherwise the file is simply renamed from '<filename>.fem' to '<filename>.dac'.

        Parameters:
        -----------
            relative : Bool, optional
                Will return absolute path if `False` (default), and relative path if `True`
        
        """
        fempath = os.path.abspath(self.doc.getProblemPath())
        folders = os.path.dirname(fempath).split(os.path.sep)
        if folders[-1] == "femdata":
            folders[-1] = "results"
            folder = os.path.sep.join(folders)
            dacpath = folder + os.path.sep + os.path.basename(fempath).replace(".fem", ".dac")
        else:
            dacpath = fempath.replace(".fem", ".dac")
            
        if relative:
            return os.path.relpath(dacpath)
        else:
            return os.path.abspath(dacpath)


    def start(self, dac=None, ui="widget",
              compact_output=False, auto_start=True, auto_stop=True,
              dashboard_callback=None, custom_termination_criterion=None):
        """
        Runs the model. Similar to doc.startSimulator but adds some features.

        Parameters
        ----------
            ui : {widget}
                The user interface. 
                `widget` will show an interactive widget, with `compact_output` = `True` a progress bar.
            dac : str or None
                Path to dacfile. if `None`, will suggest a filename.
            auto_start : Bool
                If `True` (default), will stop the simulator when finished.
            auto_stop : Bool
                If `True` (default), will stop the simulator when finished.
            dashboard_callback : BoundFunction on None
                Must be provided as a bound function with one positional parameter, which is a valid FEFLOWDocument.
                If provided, the output of this function will be displayed in the Dashboard tab of the widget.
            auto_stop: BoundFunction or None
                Must be provided as a bound function with one positional parameter, which is a valid FEFLOWDocument.
                If the return value is True, the simulation is aborted. Useful e.g. to stop a simulation when reaching
                quasi steady-state.
        """

        #TODO
        #:param dac: (not implemented)
        #:param save_time_steps: (not implemented)
        #:param skip_time_steps: (not implemented)
        #:param binary: (not implemented)
        #:param compact_output: (not implemented) - only show a progress bar.
        #:param auto_stop: auto-terminate the simulation after completion

        if ui == "widget":

            from ifm_contrib.c.simulator.Simulator import SimWidget

            if compact_output is False:
                simwidget = SimWidget(self.doc,
                                      filepath_dac=dac,
                                      dashboard_callback=dashboard_callback,
                                      custom_termination_criterion=custom_termination_criterion)
                simwidget.display()
                if auto_start:
                    simwidget.start()
                if auto_stop:
                    simwidget.stop()
            else:
                raise NotImplementedError("Sorry, widget with compact view not implemented yet. :-( Looking for volunteers!! :-)")
        else:
            raise NotImplementedError("Sorry, only widget mode available yet. :( Looking for volunteers!! :-)")


    def getAbsoluteSimulationTimeCalendar(self):
        """
        Get the current absolute simulation time as a datetime object.
        Reference time must be set in model.
        :return: DataFrame
        """
        if self.doc.getReferenceTime() is None:
            raise ValueError("Reference Time not set in FEFLOW model.")

        self.doc.getReferenceTime() + datetime.timedelta(days=self.doc.getAbsoluteSimulationTime())

    def load_first_ts_after(self, time):
        """
        Load the first time step after the time step provided by time
        :param time: Simulation time to load
        :type time: float
        :return: Information on time step loaded
        :rtype: pandas.Series
        """

        # get time step list
        df_ts = self.doc.c.sim.df.time_steps()
            
        if type(time) in [float, int]:
            if len(df_ts[df_ts.simulation_time > time]) == 0:
                raise RuntimeError("{} contains no timestep after {} d".format(self.doc.c.original_filename, time))
            else:
                ts_no = int(df_ts[df_ts.simulation_time > time].reset_index().iloc[0].file_index)
                self.doc.loadTimeStep(ts_no)
                return df_ts[df_ts.simulation_time > time].reset_index().iloc[0]
        elif type(time) == datetime:
            if len(df_ts[df_ts.simulation_date>time])==0:
                raise RuntimeError("{} contains no timestep after {}".format(self.doc.c.original_filename, time))
            else:
                ts_no = int(df_ts[df_ts.simulation_date > time].reset_index().iloc[0].file_index)
                self.doc.loadTimeStep(ts_no)
                return df_ts[df_ts.simulation_date > time].reset_index().iloc[0]
        else:
            raise ValueError("parameter 'time' must be of type float (simulation time in days)  ")

    def calendar_to_simtime(self, calendar_time):
        """
        Converts a calendar time (datetime) to simulation time (in hours).
        Requires that the Reference Time is set in the model.

        :param calendar_time: The simulation time as a calendar datetime.
        :type calendar_time:  datetime.datetime
        :return:              The time in simulation time, unit: days.
        :rtype:               float
        """
        time_ref = self.doc.getReferenceTime()

        if time_ref is None:
            raise (RuntimeError("Reference time not set in model"))

        return (calendar_time - time_ref).total_seconds() / (24 * 60 * 60)

    def simtime_to_calendar(self, sim_time):
        """
        Converts a simulation time (in unit days since reference time) into a calendar date (datetime.datetime).
        Requires that the Reference Time is set in the model.

        :param sim_time:   The time in simulation time, unit: days.
        :type sim_time:    float
        :return:           The simulation time as a calendar datetime.
        :rtype:            datetime.datetime
        """
        time_ref = self.doc.getReferenceTime()
        if time_ref is None:
            raise (RuntimeError("Reference time not set in model"))

        return time_ref + timedelta(sim_time)

