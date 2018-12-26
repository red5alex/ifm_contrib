"""
This file is planned to provides the standard FEFLOW color maps to matplotlib.
This is unfinished work, with only the standard raibow color map implemented by hard-coding.
This file is meant to import the colormaps directly from the XML files in the same folder, which have
been exported from the FEFLOW GUI.
If anybody has some time, feel free to get going.
"""

import glob, os
import xml.etree.ElementTree as ET

from matplotlib.colors import LinearSegmentedColormap
import numpy as np

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
        from matplotlib import cm
        cm.register_cmap(name, cmap)

    return cmap

# import all existing xml files, use filename as colormapname
cmaps_map = {}
local_directory = os.path.abspath(os.path.dirname(__file__))
for filename in glob.glob(local_directory + "/*.xml"):
    cmapname = os.path.split(filename)[1].replace(".xml", "")
    cmap = create_colormap_from_xml(cmapname, filename)
    cmaps_map[cmapname] = cmap
cmaps = list(cmaps_map.keys())
