from ifm import Enum

import pandas as pd
from datetime import datetime
import sys


class Simulator:
    """
    Extension child-class for IFM contributor's Extensions.
    Use this class to add functionality relating to MESH (Nodes, Elements).
    """

    def __init__(self, doc):
        self.doc = doc

    # add custom methods here
    def start(self, dac=None, save_time_steps=None, skip_time_steps=None, binary=True,
              compact_output=True, time_log_xlsx=None, auto_stop=True):
        """
        Runs the model. Similar to doc.startSimulator but adds some features.
        :param dac: (not implemented)
        :param save_time_steps: (not implemented)
        :param skip_time_steps: (not implemented)
        :param binary: (not implemented)
        :param compact_output: write console output to a single line
        :param time_log_xlsx: file name for storing time measurement data
        :param auto_stop: auto-terminate the simulation after completion
        :return:
        """

        # initialize
        clock_start = datetime.now()
        clock_now = datetime.now()
        time_elapsed = 0.
        print("simulation started at {:%m/%d/%Y, %H:%M:%S}".format(clock_start))
        t_0 = self.doc.getAbsoluteSimulationTime()
        df_log = pd.DataFrame()
        i = 0

        # run time steps
        while self.doc.getAbsoluteSimulationTime() < self.doc.getFinalSimulationTime():
            self.doc.singleStep()
            i += 1

            # measure time
            clock_now = datetime.now()
            simu_time = self.doc.getAbsoluteSimulationTime()
            time_step = self.doc.getCurrentTimeIncrement()

            # get percent progress
            t_end = self.doc.getFinalSimulationTime()
            progress = (simu_time - t_0) / (t_end - t_0)

            # write time log
            df_log = df_log.append({"i": i,
                                    "wall_time": clock_now,
                                    "simu_time": simu_time,
                                    "time_step": time_step},
                                   ignore_index=True)
            if time_log_xlsx is not None:
                df_log.to_excel(time_log_xlsx)

            # update console
            time_elapsed = clock_now - clock_start
            sys.stdout.write(
                "\r#{:4d} {: 4d}%  t={:2.2e}  dt={:2.2e}    clock={}".format(i, int(progress * 100), simu_time,
                                                                             time_step, time_elapsed))
            sys.stdout.flush()
            if not compact_output:
                print("")

        # finalize
        sys.stdout.write("\rmodel run complete {:%m/%d/%Y, %H:%M:%S} ({})".format(clock_now, time_elapsed))
        if auto_stop:
            self.doc.stopSimulator()
            sys.stdout.write(", simulator stopped")
        print(".")
