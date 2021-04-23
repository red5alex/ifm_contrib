import os
from datetime import datetime
from glob import glob

from IPython.display import display
import ipywidgets as widgets
from ipywidgets import interact, interactive

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import ifm_contrib as ifm


class SimWidget:
    """
    Creates an IPython Widget class that provides a UI for usage e.g. in Jupyter Notebooks.
    its purpose is to provide the simulator functionality of the GUI in an interactive scripting environment.

    """

    def __init__(self, doc, filepath_dac=None, dashboard_callback=None, custom_termination_criterion=None):
        """
        Create a new SimWidget class object. 
        
        :param doc: the FEFLOW Document (fem-file) to be run.
        :param filepath_dac: Name of the output file or None.
        :param dashboard_callback: a bound function to provide visualization during simulation. Called after every 
        time step. The function must accept a single positional parameter, which is the current FEFLOW document.
        :param custom_termination_criterion: a bound function that provides a custom termination criterion. Called after every 
        time step. The function must accept a single positional parameter, which is the current FEFLOW document. 
        Simulation is aborted if the function returns True. 
        """

        if ifm.getKernelVersion () < 7400:
            raise RuntimeError("This function requires FEFLOW Version 7.400 or higher!")

        self.doc = doc

        self.dashboard_callback = dashboard_callback
        self.custom_termination_criterion = custom_termination_criterion

        if filepath_dac is None:
            self.filepath_dac = doc.c.sim.suggest_dac_filename()
        else:
            self.filepath_dac = filepath_dac

        self.doc.setOutput(self.filepath_dac)

        # setup time logging
        self.df_log = pd.DataFrame()
        self.logfile = None

        # create tab layout - endpoints       
        self.tab_1 = widgets.Output()  # layout={'border': '1px dotted black'})
        self.tab_1b = widgets.Output()  # layout={'border': '1px dotted black'})
        self.tab_2 = widgets.Output()  # layout={'border': '1px dotted black'})
        self.tab_3 = widgets.Output()  # layout={'border': '1px dotted black'})

        # create tab layout - tabs
        self._tabs = widgets.Tab()
        self._tab_1 = widgets.HBox([self.tab_1, self.tab_1b])
        self._tab_2 = widgets.Box([self.tab_2])
        self._tab_3 = widgets.Box([self.tab_3])
        self._tabs.children = [self._tab_1, self._tab_2, self._tab_3]
        self._tabs.set_title(0, "Status")
        self._tabs.set_title(1, "Dashboard")
        self._tabs.set_title(2, "Computing Speed")

        # content - status tab - left side
        self.femfilename = widgets.Text(
            description="fem file",
            value=os.path.relpath(doc.getProblemPath()),
            disabled=True)

        self.dacfilename = widgets.Text(
            description="output file",
            value=os.path.relpath("./test.dac"))

        self.time_progress = widgets.FloatProgress(
            description="idle",
            min=doc.getInitialSimulationTime(),
            max=doc.getFinalSimulationTime())

        self.inttext_stepnumber = widgets.IntText(
            description="time step")

        self.out_status = widgets.widgets.HTML()
        self.out_message = widgets.widgets.HTML()

        # start, pause, stop buttons
        self.button_start = widgets.Button(description="start", layout={'width': '95px'}, disabled=False)
        self.button_start.on_click(self._start_simulator)
        self.button_pause = widgets.Button(description="pause", layout={'width': '95px'}, disabled=True)
        self.button_pause.on_click(self._pause_simulator)
        self.button_stop = widgets.Button(description="stop", layout={'width': '95px'}, disabled=True)
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

        # content - Results tab
        self.widget_results = interactive(self.plot_results)
        with self.tab_2:
            display(self.widget_results)

        # content - performance tab
        self.widget_clocktime = interactive(self.plot_walltime)
        with self.tab_3:
            display(self.widget_clocktime)

    def display(self):
        display(self._tabs)

    # plots
    def plot_hist_tsteps(self):
        doc = self.doc
        fig, ax1 = plt.subplots(1, figsize=(6, 4))
        ax1.set_xlim(doc.getInitialSimulationTime(), doc.getFinalSimulationTime())
        ax1.set_xlabel("Simulation Time [d]")
        ax1.set_ylabel("Time Step Length [d]")
        ax1.set_yscale("log")
        df = doc.c.hist.df.history(ifm.Enum.HIST_TIMES)
        ax1.plot(df, "o-")
        plt.grid()
        plt.show()

    def plot_results(self):
        # run custom code
        if self.dashboard_callback is not None:
            self.dashboard_callback(self.doc)


    def plot_walltime(self):
        doc = self.doc
        df_log = self.df_log
        # setup figure
        fig, ax1 = plt.subplots(1, figsize=(6, 4))
        ax1.set_ylim(0, doc.getFinalSimulationTime() - doc.getInitialSimulationTime())
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
            # logfile = os.path.abspath(f"./timelogger/{doc.getProblemPath()}.timelog.xlsx")
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
        self.button_start.disabled = True
        self.button_stop.disabled = False
        self.button_pause.disabled = False

        # set the results file path
        self.doc.setOutput(self.get_dac())  # TODO

        # prepare performance logging if dir ./timelogger exists
        self.logfile = None
        filename_fem = os.path.basename(self.femfilename.value)
        if os.path.isdir("./timelogger"):
            self.logfile = os.path.abspath(f"./timelogger/{os.path.basename(self.doc.getProblemPath())}.timelog.xlsx")
            # if log-file exists (from previous run), increment a suffix until until a 'free' file name is found.
            if os.path.isfile(self.logfile):
                counter = 1
                while os.path.isfile(self.logfile):
                    counter += 1
                    self.logfile = os.path.abspath(f"./timelogger/{filename_fem}-{counter}.timelog.xlsx")

        # record the starting time
        self.clock_start = datetime.now()
        clock_now = datetime.now()
        time_elapsed = 0.

        # setup time logging
        self.df_log = pd.DataFrame()

        self.time_progress.description = "running"
        self.out_status.value += "started at {:%m/%d/%Y, %H:%M:%S}<br>".format(self.clock_start)

        # commence the simulation
        t_0 = self.doc.getAbsoluteSimulationTime()
        i = 0

        simulation_state = "running"

        while self.doc.singleStep() and simulation_state=="running":
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
            self.df_log["wall_period"] = (self.df_log.wall_time - self.df_log.loc[
                0, "wall_time"]).dt.total_seconds() / 60.
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
            self.widget_results.update()

            if self.custom_termination_criterion is not None:
                if self.custom_termination_criterion(self.doc) is True:
                    simulation_state = "abort"

            # set UI to new state
        self.time_progress.description = "finished"
        self.time_progress.bar_style = 'success'
        self.button_stop.disabled = False

    def _pause_simulator(self, button):
        print("not implemented (paused)")

    def _stop_simulator(self, button):
        self.stop()

    def stop(self):
        """
        stop the simulator.
        """
        print("STOP!!")

        self.doc.stopSimulator()
        self.button_stop.disabled = True
        self.button_start.disabled = False

    def get_dac(self):
        return ("./test.dac")

    def enter_simulator(self):
        pass

    def start_simulator(self, button):
        print("simulator started")
        button.disabled = True
        self.button_stop.disabled = False
        self.button_start.disabled = True

    def pause_simulator(self, button):
        print("not implemented (paused)")

    def stop_simulator(self, button):
        self.doc.stopSimulator()
        button.disabled = True
