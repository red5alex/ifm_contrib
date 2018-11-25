"""
This file is planned to provides the standard FEFLOW color maps to matplotlib.
This is unfinished work, with only the standard raibow color map implemented by hard-coding.
This file is meant to import the colormaps directly from the XML files in the same folder, which have
been exported from the FEFLOW GUI.
If anybody has some time, feel free to get going.
"""


from matplotlib.colors import LinearSegmentedColormap
import numpy as np

feflow_rainbow = LinearSegmentedColormap.from_list("feflow_rainbow",
                                                   np.array([[0.5, 0.0, 0.5, 1.0],
                                                     [0.0, 0.0, 1.0, 1.0],
                                                     [0.0, 0.75, 0.75, 1.0],
                                                     [0.0, 1.0, 0.0, 1.0],
                                                     [1.0, 1.0, 0.0, 1.0],
                                                     [1.0, 0.0, 0.0, 1.0]]),
                                                   N=100)



# xmlfile = "./feflow_rainbow.xml"
# colors = []
# lines = open(xmlfile).readlines()
# for line in [l for l in lines if "colorItem frac" in l]:
#     words = [w.split("=")[-1].strip('"') for w in line.split()]
#     wfrac = float(words[1])
#     wr = float(words[2])
#     wg = float(words[3])
#     wb = float(words[4])
#     wa = float(words[5])
#     colors.append([wr, wg, wb, wa])