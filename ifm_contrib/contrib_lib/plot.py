import ifm_contrib as ifm
from ifm import Enum

from .plot_geopandas import PlotGpd
from .plot_folium import PlotFolium


class Plot:
    """
    Functions for creating visual plots using the matplotlib.  The function resemble the functionality of the
    View Components panel; The default plot styles are chosen to  minmic output from FEFLOW's user interface.
    Useful for visualization of the model in an interactive environments like Jupyter, or for batch processing
    of images. See examples for further info.
    """

    def __init__(self, doc):
        self.doc = doc

        # add custom child-classes here
        self.gdf = PlotGpd(doc)
        self.folium = PlotFolium(doc)

    # add custom methods here

    def _contours(self, par=None, expr=None, distr=None, velocity=None, values=None, slice=1, global_cos=True,
                  species=None, style='isolines', ignore_inactive=True, **kwargs):
        """
        Business functions for plotting library.

        :param global_cos: If True, use global coordinate system (default: local)
        :return: GeoDataFrame
        """

        import numpy as np
        import matplotlib.pyplot as plt
        import matplotlib.tri as tri

        # check if keywords arguments are corrent - dirty fix, this required reimplementation.
        if slice > self.doc.getNumberOfSlices():
            raise ValueError("no entitiy provided (either of par, distr or expr parameter must be called) or slice number out of range.")

        # set current species
        if species is not None:
            if type(species) == str:
                speciesID = self.doc.findSpecies(species)
            elif type(species) == int:
                speciesID = species
            else:
                raise ValueError("species must be string (for name) or integer (for id)")
            self.doc.setMultiSpeciesId(speciesID)

        # read incidence matrix and node coordinates
        imat = self.doc.c.mesh.get_imatrix2d(slice=slice, ignore_inactive=ignore_inactive,
                                             split_quads_to_triangles=True)
        x, y = self.doc.getParamValues(Enum.P_MSH_X), self.doc.getParamValues(Enum.P_MSH_Y)

        if global_cos:
            X0 = self.doc.getOriginX()
            Y0 = self.doc.getOriginY()
            x = [X + X0 for X in x]
            y = [Y + Y0 for Y in y]

        # create Triangulation object
        femesh = tri.Triangulation(x, y, np.asarray(imat))

        if style == "edges":
            return plt.triplot(femesh, **kwargs)
        elif style == "faces":
            from matplotlib.colors import LinearSegmentedColormap
            allgrey_cm = LinearSegmentedColormap.from_list("all_grey",
                                                           np.array([[0.5, 0.5, 0.5, 1.], [0.5, 0.5, 0.5, 1.]]))
            return plt.tripcolor(femesh, np.zeros_like(range(self.doc.getNumberOfNodes())),
                                 cmap=allgrey_cm, **kwargs)

        # get values, remove nan values (=inactive elements)
        if par is not None:
            self.doc.getParamSize(par)  # workaround for a crashbug in FEFLOW
            values = self.doc.getParamValues(par)
        elif expr is not None:
            if type(expr) == str:
                exprID = self.doc.getNodalExprDistrIdByName(expr)
            elif type(expr) == int:
                exprID = expr
            else:
                raise ValueError("expr must be string (for name) or integer (for id)")
            values = [self.doc.getNodalExprDistrValue(exprID, n) for n in range(self.doc.getNumberOfNodes())]
        elif distr is not None:
            if type(distr) == str:
                distrID = self.doc.getNodalRefDistrIdByName(distr)
            elif type(distr) == int:
                distrID = distr
            else:
                raise ValueError("distr must be string (for name) or integer (for id)")
            values = [self.doc.getNodalRefDistrValue(distrID, n) for n in range(self.doc.getNumberOfNodes())]
        elif velocity is not None:
            if velocity not in ['v_x', 'v_y', 'v_z','v_norm']:
                raise ValueError("Allowed options vor parameter 'velocity': 'v_x', 'v_y', 'v_z' or 'v_norm'")
            values = self.doc.c.mesh.df.nodes(velocity=True)[velocity]

        elif values is not None:
            values = values  # OK, so this is just to make clear that we are using the values directly!
        else:
            raise ValueError("either of parameter par, expr or distr must be provided!")

        # set nan values to zero
        values = np.nan_to_num(np.asarray(values))

        # generate polygons from matplotlib (suppress output)
        if style == "continuous":
            return plt.tripcolor(femesh, values,
                                 shading='gouraud', **kwargs)
        elif style == "patches":
            try:
                return plt.tripcolor(femesh, facecolors=values.flatten(),
                                 **kwargs)
            except ValueError as e:
                # problems with quad elements --> need to have values for split elements, was
                # not a poblem for nodal values...
                if "Length of color" in str(e):
                    raise NotImplementedError("This function does not support quad elements yet")
                else:
                    raise e

        elif style == "fringes":
            contourset = plt.tricontourf(femesh, values, **kwargs)
            return contourset
        elif style == "isolines":
            contourset = plt.tricontour(femesh, values, **kwargs)
            return contourset
        else:
            raise ValueError("unkonwn style " + str(style))

    def faces(self, color="grey", alpha=1.0, ignore_inactive=False, *args, **kwargs):
        """
        Add the faces of the model to the plot.
        Corresponds to the geometrie : faces style in FEFLOW.
        """
        return self._contours(*args, style="faces", ignore_inactive=ignore_inactive,
                              color=color, alpha=alpha, **kwargs)

    def edges(self, color="black", alpha=0.5, lw=1, ignore_inactive=False, *args, **kwargs):
        """
        Add the edges of the mesh to the plot.
        Corresponds to the geometrie > edges style in FEFLOW.
        """
        return self._contours(*args, style="edges", ignore_inactive=ignore_inactive,
                              color=color, alpha=alpha, lw=lw, **kwargs)

    def continuous(self, slice=1, alpha=0.5, cmap="feflow_rainbow", *args, **kwargs):
        """
        Add an interpolated color plot of the given nodal model property to the plot.
        Corresponds to the continuous style in FEFLOW.
        Note: Avoid usage when creating vector graphics (svg).

        :param slice: specified the slice to be plotted in a 3D model.
        :type slice: int
        :param args: see matplotlib.org/api/_as_gen/matplotlib.axes.Axes.tripcolor.html
        :param kwargs: matplotlib.org/api/_as_gen/matplotlib.axes.Axes.tripcolor.html
        """
        return self._contours(*args, style="continuous", slice=slice,
                              cmap=cmap, alpha=alpha, **kwargs)

    def fringes(self, slice=1, alpha=0.5, cmap="feflow_rainbow", *args, **kwargs):
        """
        Add fringe polygons of the given nodal model property to the plot.
        Corresponds to the fringes style in FEFLOW.

        :param slice: specified the slice to be plotted in a 3D model.
        :type slice: int
        :return: matplotlib.contour.ContourSet
        """
        return self._contours(*args, style="fringes", slice=slice,
                              cmap=cmap, alpha=alpha, **kwargs)

    def isolines(self, slice=1, alpha=1.0, *args, **kwargs):
        """
        Add isolines of the given nodal model property to the plot.
        Corresponds to the Isolines style in FEFLOW.

        :param slice: specified the slice to be plotted in a 3D model.
        :type slice: int
        :return: matplotlib.contour.ContourSet
        """
        return self._contours(*args, style="isolines", slice=slice,
                              alpha=alpha, **kwargs)

    def obs_markers(self, color="lightgreen", filter_by=None, *args,  **kwargs):
        """
        Add observation point markers to the plot.
        Corresponds to Obs. Markers in FEFLOW.

        :param args:   arguments for plt.scatter
        :param kwargs: arguments for plt.scatter
        :return:
        """

        import matplotlib.pyplot as plt

        self.doc.c.obs.gdf.obspoints(filter_by=filter_by).plot(ax=plt.gca(), color=color)

    def obs_labels(self, attribute='label', horizontalalignment='center', filter_by=None, *args, **kwargs):
        """
        Add observation point labels to the plot.
        Corresponds to Obs. Labels in FEFLOW.

        :param attribute: "label", "x", "y", "node" or "h" (modelled head)
        :type attribute:  str
        :param args:      arguments for plt.annotate
        :param kwargs:    arguments for plt.annotate
        :return:
        """

        import matplotlib.pyplot as plt

        for i, row in self.doc.c.obs.gdf.obspoints(filter_by=filter_by).iterrows():
            plt.annotate(*args, row[attribute],
                         xy=(row.x, row.y),
                         horizontalalignment=horizontalalignment,
                         **kwargs)

    def patches(self, layer=1, alpha=0.5, cmap="feflow_rainbow", *args, **kwargs):
        """
        Add plot of the given elemental model property to the plot.
        Corresponds to the patches style in FEFLOW (for elemental property).
        Note: Avoid usage when creating vector graphics (svg).

        :param slice: specified the slice to be plotted in a 3D model.
        :type slice: int
        :param args: see matplotlib.org/api/_as_gen/matplotlib.axes.Axes.tripcolor.html
        :param kwargs: matplotlib.org/api/_as_gen/matplotlib.axes.Axes.tripcolor.html
        """

        # TODO:
        #
        # gdf_zones = doc.c.plot.gdf.patches().dissolve(PROPERTY)
        # gdf_zones["repr_point"] = gdf_zones.geometry.apply(lambda x: x.representative_point().coords[:])
        # gdf_zones['repr_point'] = [coords[0] for coords in gdf_zones['repr_point']]
        # for idx, row in gdf_zones.iterrows():
        #     plt.annotate(s=PROPERTY, xy=row['repr_point'],
        #                  horizontalalignment='center')

        return self._contours(*args, style="patches", slice=layer,
                              cmap=cmap, alpha=alpha, **kwargs)

    def borders(self, ax=None, *args, **kwargs):
        self.doc.c.mesh.gdf.borders().plot(ax=ax, *args, **kwargs)


    def _zoom_to(self, selection, ax=None, zoom=1.):
        minx, maxx, miny, maxy = get_XYbounds(self, selection)

        # get axis and adjust limits
        if ax is None:
            ax = plt.gca()
        ax.set_xlim(minx, maxx)
        ax.set_ylim(miny, maxy)