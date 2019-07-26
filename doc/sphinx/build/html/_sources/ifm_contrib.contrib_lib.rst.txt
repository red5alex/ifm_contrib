Content
=======

**Accessing Nodal and Elemental Model Data**

+ :ref:`doc.c.mesh<doc.c.mesh - Model Properties>` :ref:`(.df<doc.c.mesh.df - Model Properties (Pandas)>` / :ref:`.gdf<doc.c.mesh.gdf - Model Properties (Geopandas)>`): Generate lists / DataFrames of nodes and elements (including parameter values), Discrete Feature Elements, Multi-Layer-Wells and more.
+ :ref:`doc.c.sel<doc.c.sel - Selections>`: Query information and item lists of elemental and nodal selections. Also provides operations like conversions.
+ :ref:`doc.c.content<doc.c.content.df - Content (Pandas)>`: Get *Content Panel* readouts as DataFrame.

**Plotting and Visualization**

+ :ref:`doc.c.plot<doc.c.plot.gdf - Plot Output>`: Create 2D matplotlib figures similar to the Slice View. Supports a number of items known from the *View Components Panel* of the GUI. Default settings are chosen to mimic the appearance of the FEFLOW GUI (including colormaps). 
+ :ref:`doc.c.plot.gdf<doc.c.plot.gdf - Plot Output>`: Create fringes and isolines as vector data (GeoDataFrames). Similar to the *export plots...* function of the View Components Panel.

**History charts and Time Series**

+ :ref:`doc.c.hist.df (Pandas only)<doc.c.hist.df - History Charts>`: Query *History Charts* from dac-files as DataFrames.
+ :ref:`doc.c.ts<doc.c.ts - Time Series>` (:ref:`.df<doc.c.ts - Time Series (Pandas)>`): Get information and content of *Time Series*.

**Observation Points**

+ :ref:`doc.c.obs.gdf<doc.c.obs.gdf - Observations (Geopandas)>`: get observatoin point information as GeoDataFrames


Accessing Nodal and Elemental Model Data
========================================


doc.c.mesh - Model Properties
-----------------------------

.. automodule:: ifm_contrib.contrib_lib.mesh
    :members:
    :undoc-members:
	
doc.c.mesh.df - Model Properties (Pandas)
-----------------------------------------

.. automodule:: ifm_contrib.contrib_lib.mesh_pandas
    :members:
    :undoc-members:
	
doc.c.mesh.gdf - Model Properties (Geopandas)
---------------------------------------------

.. automodule:: ifm_contrib.contrib_lib.mesh_geopandas
    :members:
    :undoc-members:
	
doc.c.sel - Selections
----------------------

.. automodule:: ifm_contrib.contrib_lib.sel
    :members:
    :undoc-members:

doc.c.content.df - Content (Pandas)
-----------------------------------

.. automodule:: ifm_contrib.contrib_lib.content_pandas
    :members:
    :undoc-members:		
	
Plotting and Visualization
==========================	
	
These objects provide functionality to create plots of the model.
These are mostly used in interactive scripting environments like Jupyter or Spyder.	

doc.c.plot - Matplotlib
-----------------------

.. automodule:: ifm_contrib.contrib_lib.plot
    :members:
    :undoc-members:
	
doc.c.plot.gdf - Plot Output
----------------------------

.. automodule:: ifm_contrib.contrib_lib.plot_geopandas
    :members:
    :undoc-members:
	
History Charts and Time Series
==============================


doc.c.hist.df - History Charts
--------------------------------

.. automodule:: ifm_contrib.contrib_lib.hist_pandas
    :members:
    :undoc-members:
	
doc.c.ts - Time Series
---------------------------

.. automodule:: ifm_contrib.contrib_lib.ts
    :members:
    :undoc-members:
	
doc.c.ts - Time Series (Pandas)
------------------------------------

.. automodule:: ifm_contrib.contrib_lib.ts_pandas
    :members:
    :undoc-members:


Observation Points
==================

doc.c.obs.gdf - Observations (Geopandas)
----------------------------------------

.. automodule:: ifm_contrib.contrib_lib.obs_geopandas
    :members:
    :undoc-members:


[sphinx:ifm_contrib.contrib_lib.rst]
