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

    class SimWidget:

        def __init__(self, doc, filepath_dac=None):
            from IPython.display import display
            import ipywidgets as widgets
            from ipywidgets import interact, interactive

            self.doc = doc

            if filepath_dac is None:
                self.filepath_dac = doc.c.sim.suggest_dac_filename()
            else:
                self.filepath_dac = filepath_dac
            
            # setup time logging
            self.df_log = pd.DataFrame()
            self.logfile = None
            
            # create tab layout - endpoints       
            self.tab_1 = widgets.Output()  # layout={'border': '1px dotted black'})
            self.tab_1b = widgets.Output() # layout={'border': '1px dotted black'})
            self.tab_2 = widgets.Output()  # layout={'border': '1px dotted black'})
            self.tab_3 = widgets.Output()  # layout={'border': '1px dotted black'})

            # create tab layout - tabs
            self._tabs = widgets.Tab()
            self._tab_1 = widgets.HBox([self.tab_1, self.tab_1b])
            self._tab_2 = widgets.Box([self.tab_2])
            self._tab_3 = widgets.Box([self.tab_3])
            self._tabs.children = [self._tab_1, self._tab_2, self._tab_3]
            self._tabs.set_title(0, "Status")
            self._tabs.set_title(1, "Results")
            self._tabs.set_title(2, "Computing Speed")
        
            # content - status tab - left side
            self.femfilename = widgets.Text(
                description="fem file",
                value=os.path.relpath(doc.getProblemPath()),
                disabled=True)

            self.dacfilename = widgets.Text(
                description="output file",
                value = os.path.relpath("./test.dac"))

            self.time_progress = widgets.FloatProgress(
                description = "idle",
                min = doc.getInitialSimulationTime(),                               
                max = doc.getFinalSimulationTime())

            self.inttext_stepnumber = widgets.IntText(
                description = "time step")

            self.out_status = widgets.widgets.HTML()
            self.out_message = widgets.widgets.HTML()

            # start, pause, stop buttons
            self.button_start = widgets.Button(description="start", layout={'width': '95px'}, disabled=False)
            self.button_start.on_click(self._start_simulator)
            self.button_pause = widgets.Button(description="pause", layout={'width': '95px'}, disabled=True)
            self.button_pause.on_click(self._pause_simulator)
            self.button_stop  = widgets.Button(description="stop",  layout={'width': '95px'}, disabled=True)
            self.button_stop.on_click(self._stop_simulator)
            
            with self.tab_1:
                display(self.femfilename)
                display(self.dacfilename)
                display(self.time_progress)
                display(self.inttext_stepnumber)
                display(widgets.HBox([self.button_start, self.button_pause, self.button_stop]))
                display(self.out_status)

            # content - status tab - right side (time step history)
            self.widget_tsteplist = interactive(self.plot_hist_tsteps)   
            with self.tab_1b:
                display(self.widget_tsteplist)
            
            # content - performance tab
            self.widget_clocktime = interactive(self.plot_walltime)  
            with self.tab_3:
                display(self.widget_clocktime)

        def display(self):
            display(self._tabs)
        
        # plots
        def plot_hist_tsteps(self):
            doc = self.doc
            fig, ax1 = plt.subplots(1, figsize = (6,4))
            ax1.set_xlim(doc.getInitialSimulationTime(), doc.getFinalSimulationTime())
            ax1.set_xlabel("Simulation Time [d]")
            ax1.set_ylabel("Time Step Length [d]")
            ax1.set_yscale("log")
            df=doc.c.hist.df.history(Enum.HIST_TIMES)
            ax1.plot(df, "o-")
            plt.grid()
            plt.show()
            
        def plot_walltime(self):
            doc = self.doc
            df_log = self.df_log
            # setup figure
            fig, ax1 = plt.subplots(1, figsize = (6,4))
            ax1.set_ylim(0, doc.getFinalSimulationTime()-doc.getInitialSimulationTime())
            ax1.set_xlabel("Wall Clock Time [min]")
            ax1.set_ylabel("Simulation Time [d]")   
            plt.grid()
            # plot the logged time, if exists
            if len(df_log) > 0:
                ax1.plot(df_log.set_index("wall_period").sim_period, 
                        ".-",
                        label="this simulation")
            # if performance log-files are found, show them, too
            if os.path.isdir("./timelogger"):
                #logfile = os.path.abspath(f"./timelogger/{doc.getProblemPath()}.timelog.xlsx") 
                for f in glob("./timelogger/*.timelog.xlsx"):
                    if self.logfile is not None and os.path.samefile(f, self.logfile):
                        continue
                    df_compare = pd.read_excel(f)
                    plt.plot(df_compare.set_index("wall_period").sim_period, "--", 
                            label=os.path.basename(f).replace(".timelog.xlsx", ""),
                            alpha=0.4, linewidth=0.8)
            # show legend if a legend, and finalize.
            if len(df_log) > 0 or len(glob("./timelogger/*.timelog.xlsx")) > 0:
                plt.legend()
            plt.show()
                
        def _start_simulator(self, button):
            # relay for UI button
            self.start()
        
        def start(self):
            """
            Start the simulation
            """
            # update UI state
            self.button_start.disabled=True
                    
            # set the results file path
            self.doc.setOutput(self.get_dac())  # TODO
            
            # prepare performance logging if dir ./timelogger exists
            self.logfile = None
            filename_fem = os.path.basename(self.femfilename.value)
            if os.path.isdir("./timelogger"):
                self.logfile =  os.path.abspath(f"./timelogger/{os.path.basename(self.doc.getProblemPath())}.timelog.xlsx")
                # if log-file exists (from previous run), increment a suffix until until a 'free' file name is found.
                if os.path.isfile(self.logfile):
                    counter = 1
                    while os.path.isfile(self.logfile):
                        counter+=1
                        self.logfile =  os.path.abspath(f"./timelogger/{filename_fem}-{counter}.timelog.xlsx")
        
            # record the starting time
            self.clock_start = datetime.now()
            clock_now = datetime.now()
            time_elapsed = 0.
            
            # setup time logging
            self.df_log = pd.DataFrame()

            self.time_progress.description="running"
            self.out_status.value += "started at {:%m/%d/%Y, %H:%M:%S}<br>".format(self.clock_start)

            # commence the simulation
            t_0 = self.doc.getAbsoluteSimulationTime()
            i = 0
            while self.doc.singleStep():
                i += 1

                # measure time
                clock_now = datetime.now()
                simu_time = self.doc.getAbsoluteSimulationTime()
                time_step = self.doc.getCurrentTimeIncrement()

                # get percent progress
                t_end = self.doc.getFinalSimulationTime()
                progress = (simu_time - t_0) / (t_end - t_0)

                # write time log
                self.df_log = self.df_log.append({"i": i,
                                        "wall_time": clock_now,
                                        "simu_time": simu_time,
                                        "time_step": time_step},
                                    ignore_index=True)
                self.df_log["wall_period"] = (self.df_log.wall_time - self.df_log.loc[0, "wall_time"]).dt.total_seconds() / 60.
                self.df_log["sim_period"] = self.df_log.simu_time - self.df_log.loc[0, "simu_time"]

                # save to dataframe to excel if logging is active
                if self.logfile is not None:         
                    self.df_log.to_excel(self.logfile)

                # widget updates
                time_elapsed = clock_now - self.clock_start
                self.out_status.value = "{} steps completed in {}".format(i, time_elapsed)

                self.time_progress.value = self.doc.getAbsoluteSimulationTime()

                # update charts
                self.widget_tsteplist.update()
                self.widget_clocktime.update()   

            # set UI to new state
            self.time_progress.description="finished"
            self.time_progress.bar_style='success' 
            self.button_stop.disabled=False

            
        def _pause_simulator(self, button):
            print("not implemented (paused)")
            
        def _stop_simulator(self, button):
            self.stop()
        
        def stop(self):
            """
            stop the simulator.
            """
            self.doc.stopSimulator()
            self.button_stop.disabled=True
            self.button_start.disabled=False
            
        def get_dac(self):
            return("./test.dac")
            
        def enter_simulator(self):
            pass
        
        def start_simulator(self, button):
            print("simulator started")
            button.disabled=True
            
        def pause_simulator(self, button):
            print("not implemented (paused)")
            
        def stop_simulator(self, button):
            self.doc.stopSimulator()
            button.disabled=True
    
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
            if compact_output is False:
                simwidget = self.doc.c.sim.SimWidget(self.doc)
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
