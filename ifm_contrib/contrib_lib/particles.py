from datetime import datetime, timedelta
from time import sleep

import numpy as np
import pandas as pd
from shapely.geometry import Point
import geopandas as gpd

from ifm import Enum


class ParticleTracer:
    """
    Functions for working with selections.
    """

    def __init__(self, doc):
        self.doc = doc

        # add custom child-classes here
        self.Particle = Particle
        self.ParticleSwarm = ParticleSwarm

    def particle(self, seed_point, time_start=None,
                 forward=False, unsteady=False, random_walk=False, settings=None,
                 global_cos=True, geodataframe=True):
        """
        Creates a single particle object

        :param seed_point:
        :param time_start:
        :param settings:
        :param global_cos:
        :param geodataframe:
        :return:
        """

        return Particle(self.doc, seed_point=seed_point, time_start=time_start,
                        forward=forward, unsteady=unsteady, random_walk=random_walk, settings=settings,
                        global_cos=global_cos, geodataframe=geodataframe)

    def particle_swarm(self, forward=False, unsteady=False, random_walk=False,  default_settings=None):
        """
        Creates a ParticleSwarm object

        :param default_settings:
        :return:
        """
        return ParticleSwarm(self.doc, forward=forward, unsteady=unsteady, random_walk=random_walk,
                             default_settings=default_settings)



class Particle:
    """
    The Particle Class describes a single particle to be traced. It can be use stand-alone, or might be

    See also:
    doc.c.pt.get_particle(), ParticeSwarm()
    """

    def __init__(self, doc, seed_point, time_start=None,
                 forward=False, unsteady=False, random_walk=False, settings=None,
                 global_cos=True,
                 geodataframe=True):
        """
        Creates a particle from its seed_point and -time.
        """

        # PARAMETER HANDLING

        self.doc = doc

        if type(seed_point) == Point:
            self.seed_point = seed_point
            self.seed_x = seed_point.x
            self.seed_y = seed_point.y
            if seed_point.has_z:
                self.seed_z = seed_point.z
            else:
                self.seed_z = None
        elif type(seed_point) == tuple:
            self.seed_x = seed_point[0]
            self.seed_y = seed_point[1]
            if len(seed_point) == 3:
                self.seed_z = seed_point[2]
                self.seed_point = Point(self.seed_x, self.seed_y, self.seed_z)
            else:
                self.seed_z = None
                self.seed_point = Point(self.seed_x, self.seed_y)
        else:
            ValueError(f"seed_point of type {type(seed_point)} not supported")

        self.time_start = time_start

        # convert to local COS
        if global_cos:
            self.seed_x -= self.doc.getOriginX()
            self.seed_y -= self.doc.getOriginY()

        # IMPLEMENTATION

        # create the particle tracer
        self.pt = self.doc.createParticleTracer()

        # apply settings:
        if settings is None:
            settings = {}

        if "tracking_direction" not in settings.keys():
            if forward:
                settings["tracking_direction"] = Enum.PT_DIR_FORWARD
            else:
                settings["tracking_direction"] = Enum.PT_DIR_BACKWARD

        if "tracking_mode" not in settings.keys():
            if unsteady:
                settings["tracking_mode"] = Enum.PT_MODE_UNSTEADY
            else:
                settings["tracking_mode"] = Enum.PT_MODE_STEADY

        if "tracking_type" not in settings.keys():
            if random_walk:
                settings["tracking_type"] = Enum.PT_TYPE_RW
            else:
                settings["tracking_type"] = Enum.PT_TYPE_ADVECTIVE

        if "tracking_mode" in settings.keys():
            self.pt.setTrackingMode(settings["tracking_mode"])
        if "tracking_direction" in settings.keys():
            self.pt.setTrackingDirection(settings["tracking_direction"])
        if "tracking_type" in settings.keys():
            self.pt.setTrackingType(settings["tracking_type"])

        # set start time
        if time_start is not None:
            # convert to days if datetime is provided

            if type(time_start) is datetime or pd.Timestamp:
                time_start = doc.c.sim.calendar_to_simtime(time_start)

            # set start time
            self.pt.setInitialTime(time_start)

            if self.pt.getTrackingMode() == Enum.PT_MODE_STEADY and doc.getTimeClass() != Enum.TCLS_STEADY:
                doc.c.sim.load_first_ts_after(time_start)

        # generate pathline and load into DataFrame
        if self.seed_z is None:
            self.pl = self.pt.generatePathLine(self.seed_x, self.seed_y)
        else:
            self.pl = self.pt.generatePathLine(self.seed_x, self.seed_y, self.seed_z)

        if self.doc.getNumberOfDimensions() == 2:
            self.df = pd.DataFrame(self.pl, columns=["x", "y", "tau"])
            self.df["z"] = None
        else:
            self.df = pd.DataFrame(self.pl, columns=["x", "y", "z", "tau"])

        # convert to global COS
        if global_cos:
            self.df.x = self.df.x + self.doc.getOriginX()
            self.df.y = self.df.y + self.doc.getOriginY()

        # add sim_time and calendar axis
        self.df["sim_time"] = self.df.tau + time_start
        if self.doc.getReferenceTime() is not None:
            self.df["calendar"] = self.doc.getReferenceTime() + self.df.sim_time.apply(timedelta)



            # create geometric objects
        if geodataframe:

            # ATTENTION: THIS MIGHT CAUSE ISSUES IF IFM HAS BEEN IMPORTED PREVIOUSLY
            # ADD except ImportError if this comes up = error should advise to import geopandas in main script

            # convert points to GeoDataFrame
            self.gdf = gpd.GeoDataFrame(self.df,
                                        geometry=gpd.points_from_xy(self.df.x, self.df.y))

            # create a shapely LineString geometry from
            from shapely.geometry import LineString
            self.trajectory = LineString(self.df.geometry)
        else:
            self.gdf = None
            self.trajectory = None

    def get_location_seed_point(self):
        if self.gdf is not None:
            return self.gdf.iloc[0]
        else:
            return self.df.iloc[0]

    def get_location_at_time(self, time, geodataframe=True):
        """
        Determines the position of the particle at a particular point in time, or list of points in time
        Parameter time can be of type datetime (if )
        """

        # TODO: Series or Index as input
        # TODO: Simulation time as input

        # recursive loop:
        if type(time) == list:
            # list all Particle locations at the desired time in a dataframe
            df = pd.DataFrame([self.get_location_at_time(i, False) for i in time])

            # add geometries if geodataframe is set:
            if geodataframe:
                df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.x, df.y))
            return df

        # recursive call
        elif type(time) == datetime or pd.Timestamp:
            # raise error if there is no defined reference time
            if self.doc.getReferenceTime() is None:
                raise RuntimeError("Reference Time is not set in model.")

            # if the exact time does already exist, simply return the row
            if np.datetime64(time) in self.df.calendar.values:
                row = self.df.set_index("calendar").loc[time]
            else:
                # add the time point into the index, then interpolate over the gap and return the row
                row = \
                self.df.set_index("calendar").append(pd.DataFrame(index=[time])).sort_index(ascending=True).interpolate(
                    method="time").loc[time]

            if self.doc.c.sim.calendar_to_simtime(time) > self.df.sim_time.max():
                row["arrived"] = True
            else:
                row["arrived"] = False

            return row
        else:
            raise ValueError(f"argument time of type {type(time)} not supported.")

    def plot(self):
        # TODO: add plot function
        pass


class ParticleSwarm:
    """


    """

    def __init__(self, doc, forward=False, unsteady=False, random_walk=False, default_settings=None):

        self.particles = []
        self.doc = doc

        if default_settings is None:
            default_settings = {}

        if "tracking_direction" not in default_settings.keys():
            if forward:
                default_settings["tracking_direction"] = Enum.PT_DIR_FORWARD
            else:
                default_settings["tracking_direction"] = Enum.PT_DIR_BACKWARD

        if "tracking_mode" not in default_settings.keys():
            if unsteady:
                default_settings["tracking_mode"] = Enum.PT_MODE_UNSTEADY
            else:
                default_settings["tracking_mode"] = Enum.PT_MODE_STEADY

        if "tracking_type" not in default_settings.keys():
            if random_walk:
                default_settings["tracking_type"] = Enum.PT_TYPE_RW
            else:
                default_settings["tracking_type"] = Enum.PT_TYPE_ADVECTIVE

        self.default_settings = default_settings

    def append_particle(self, seed_point, time_start=None, global_cos=True, settings=None,
                        count=1, delay=0, progress_indicator=None):

        # use default settings of ensemble if no setting is provided
        if settings is None:
            settings = self.default_settings

        # get x,y,z from seedpoint
        if type(seed_point) == tuple:
            if len(seed_point) == 2:
                x, y = seed_point
                z = None
            elif len(seed_point) == 3:
                x, y, z = seed_point
            else:
                raise ValueError("seed_point of type tuple must have length 2 or 3!")

        # get x,y,z from shapely.geometry.Point
        elif type(seed_point) == Point:
            x = seed_point.x
            y = seed_point.y
            if seed_point.has_z:
                z = seed_point.z
            else:
                z = None
        else:
            raise ValueError(f"seed_point of type {type(seed_point)} not supported!")

        # some error checks
        assert type(x) == int or float, "x is not float"
        assert type(y) == int or float, "y is not float"
        if z is not None:
            assert type(z) == int or float, "z is not float"

        new_particle = Particle(self.doc, seed_point=seed_point, time_start=time_start, global_cos=global_cos,
                                settings=settings)

        self.particles.append(new_particle)

        # wait for random seed to be updated - required to fix an issue with the RW particles
        if delay is not None and delay > 0:
            sleep(delay)

        # repeat if multiple instances are desired
        if count > 1:
            # recursively start the next particle
            self.append_particle(seed_point=seed_point, time_start=time_start,
                                 global_cos=global_cos, settings=settings,
                                 count=count - 1, delay=delay)

        # update the progress indicator if provided
        if progress_indicator is not None:
            progress_indicator.value += 1
            progress_indicator.description = f"{progress_indicator.value} / {count}"

    def particle_tips(self):
        pass
        # TODO

    def particle_position_at_time(self, time, remove_arrived=False):
        """
        Returns a (Geo)DataFrame with the location of all particles at a particular time
        """
        df_location = pd.concat([pl.get_location_at_time([time]) for pl in self.particles])
        df_location.reset_index(inplace=True)
        df_location.index.name = "particle_id"

        if remove_arrived:
            return df_location[~df_location.arrived]
        else:
            return df_location

    def seed_points(self):
        """
        Returns a (Geo)DataFrame with the location of the seed points of all particles
        """

        df_seedpoints = pd.concat([p.get_location_seed_point() for p in self.particles], axis=1).T.reset_index().drop(
            "index", axis=1).set_geometry("geometry")
        df_seedpoints.index.name = "particle_id"
        return df_seedpoints

    def trajectories(self):
        """
        Return a (Geo)DataFrame with the trajectories (line-shaped) of all particles
        """

        gdf_trajectories = gpd.GeoDataFrame(geometry=[p.trajectory for p in self.particles])
        gdf_trajectories["length"] = [g.length for i, g in gdf_trajectories.geometry.iteritems()]

        gdf_trajectories.index.name = "particle_id"

        return gdf_trajectories
