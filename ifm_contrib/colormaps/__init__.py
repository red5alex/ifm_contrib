"""
This file is planned to provides the standard FEFLOW color maps to matplotlib.
This is unfinished work, with only the standard raibow color map implemented by hard-coding.
This file is meant to import the colormaps directly from the XML files in the same folder, which have
been exported from the FEFLOW GUI.
If anybody has some time, feel free to get going.
"""

import glob, os
import xml.etree.ElementTree as ET
import ifm_contrib as ifm

try:
    from matplotlib.colors import LinearSegmentedColormap
except Exception:
    raise ImportError("No module named matplotlib.colors")

def create_colormap_from_xml(name, xmlfile, register_cmap=True):
    """
    Create a new Matplotlib Colormap from a FEFLOW colormap file (XML).
    The XML file can be created from the FEFLOW GUI (export colormap).

    :param name: name of the colormap
    :type name: str
    :param xmlfile: path to the xml file.
    :type xmlfile: str
    :param register_cmap: If True (default), colormap is registered for use in matplotlib.
    :type register_cmap: bool
    :return:
    """

    tree = ET.parse(xmlfile)
    root = tree.getroot()

    colors = []
    for child in root:
        if child.tag == "colorItems":
            for colorItem in child:
                if colorItem.tag == "colorItem":
                    frac = float(colorItem.attrib["fraction"])
                    r = float(colorItem.attrib["R"])
                    g = float(colorItem.attrib["G"])
                    b = float(colorItem.attrib["B"])
                    a = float(colorItem.attrib["A"])
                    colors.append((frac, [r, g, b, a]))

    cmap = LinearSegmentedColormap.from_list(name, colors)

    if register_cmap:
        import matplotlib
        matplotlib.colormaps.register(cmap, name=name)

    return cmap

# import all existing xml files, use filename as colormapname
cmaps_map = {}
local_directory = os.path.abspath(os.path.dirname(__file__))
for filename in glob.glob(local_directory + "/*.xml"):
    cmapname = os.path.split(filename)[1].replace(".xml", "")
    cmap = create_colormap_from_xml(cmapname, filename)
    cmaps_map[cmapname] = cmap
cmaps = list(cmaps_map.keys())


def plot_feflow_colorgradients():
    """
    This code was adapted from
    https://matplotlib.org/examples/color/colormaps_reference.html
    """

    import numpy as np
    import matplotlib.pyplot as plt

    cmaps = [('FEFLOW ',
                ifm.colormaps.cmaps),]

    nrows = max(len(cmap_list) for cmap_category, cmap_list in cmaps)
    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))


    def plot_color_gradients(cmap_category, cmap_list, nrows):
        fig, axes = plt.subplots(nrows=nrows)
        fig.subplots_adjust(top=0.95, bottom=0.01, left=0.2, right=0.99)
        axes[0].set_title(cmap_category + ' colormaps', fontsize=14)

        for ax, name in zip(axes, cmap_list):
            ax.imshow(gradient, aspect='auto', cmap=plt.get_cmap(name))
            pos = list(ax.get_position().bounds)
            x_text = pos[0] - 0.01
            y_text = pos[1] + pos[3]/2.
            fig.text(x_text, y_text, name, va='center', ha='right', fontsize=10)

        # Turn off *all* ticks & spines, not just the ones with colormaps.
        for ax in axes:
            ax.set_axis_off()


    for cmap_category, cmap_list in cmaps:
        plot_color_gradients(cmap_category, cmap_list, nrows)

    plt.show()