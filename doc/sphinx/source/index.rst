.. ifm_contrib documentation master file, created by
   sphinx-quickstart on Thu Dec 20 18:52:00 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

FEFLOW ifm_contrib
=======================================

An Open-Source Extension to FEFLOW's Python programming API.

Code-Compatibility with Classic IFM
-----------------------------------

ifm_contrib inherits all commands of the classic IFM API, thus that it is code-compatible with 
code written for the classic IFM:

  ``import ifm_contrib as ifm``
  
  ``doc = ifm.loadDocument("myfeflowmodel.fem")``
  
  ``doc.getNumberOfElements()``
  
Additional Features
-------------------

It adds however additional API features, such as creating plots similar to those of the FEFLOW Slice View using matplotlib, or exporting model data to Pandas (Geo-)DataFrames.

  ``doc.c.plot.edges()``
  
  ``doc.c.hist.df.HEAD``
 

The main components are 

* ``doc.c.plot`` : **plot maps** using matplotlib, similar to FEFLOWs slice view.
* ``doc.c.hist`` : get **history chart** data
* ``doc.c.mesh`` : get **model data** (nodal, elemental, dfe, multi-layer wells, etc.)
* ``doc.c.ts`` : get **time series** data
* ``doc.c.obs`` : get **observation points** data
* ``doc.c.sel`` : get **selection** data
* ``doc.c.content`` : get **elemental content** data

Most of these modules feature Pandas and/or GeoPandas submodules for exporting the requested data directly into DataFrames and GeoDataFrames, respectively:

  ``doc.c.mesh.df.nodes(par={"HEAD" : Enum.P_HEAD})``
  ``doc.c.mesh.gdf.elements(par={"CONDX" : Enum.P_CONDX})``


For detailed information, see :ref:`modindex`.

:ref:'contrib_list'


.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   reference/modules
   tutorials
   ifm_contrib.contrib_lib
   

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
