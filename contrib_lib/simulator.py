from ifm import Enum
from .simulator_pandas import SimPd

import sys
import os

from datetime import datetime
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
        
    # add custom methods here
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
            dacpath = fempath
            
        if relative:
            return os.path.relpath(dacpath)
        else:
            return os.path.abspath(dacpath)


    def start(self, dac=None, ui="widget", 
                compact_output=False, auto_start=True, auto_stop=True):
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
                simwidget = SimWidget(self.doc)
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

        if type(time) == float or int:

            # get time step list
            df_ts = self.doc.c.sim.df.time_steps()
            if len(df_ts[df_ts.simulation_time > time]) == 0:
                raise RuntimeError("{} contains no timestep after {} d".format(self.doc.c.original_filename, time))
            else:
                ts_no = int(df_ts[df_ts.simulation_time > time].reset_index().iloc[0].file_index)
        else:
            raise ValueError("parameter 'time' must be of type float (simulation time in days)  ")

        self.doc.loadTimeStep(ts_no)
        return df_ts[df_ts.simulation_time > time].reset_index().iloc[0]
