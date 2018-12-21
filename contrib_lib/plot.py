import ifm_contrib as ifm
from ifm import Enum

from .plot_geopandas import PlotGpd


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

    # add custom methods here

    def _contours(self, par=None, expr=None, distr=None, slice=1, global_cos=True, species=None,
                  style='isolines', ignore_inactive=True, **kwargs):
        """
        Business functions for plotting library.

        :param global_cos: If True, use global coordinate system (default: local)
        :return: GeoDataFrame
        """

        import numpy as np
        import matplotlib.pyplot as plt
        import matplotlib.tri as tri

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
        else:
            raise ValueError("either of parameter param, expr or distr must be provided!")

        # set nan values to zero
        values = np.nan_to_num(np.asarray(values))

        # generate polygons from matplotlib (suppress output)
        if style == "continuous":
            return plt.tripcolor(femesh, values,
                                 shading='gouraud', **kwargs)
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

    def continuous(self, slice=1, alpha=0.5, cmap=ifm.colormaps.feflow_rainbow, *args, **kwargs):
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

    def fringes(self, slice=1, alpha=0.5, cmap=ifm.colormaps.feflow_rainbow, *args, **kwargs):
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
