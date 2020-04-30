# ifm_contrib

An Open Source Extension Project for the FEFLOW Programming API.

ifm_ contrib is an Open-Source Extension of the IFM. It is written by FEFLOW users, for FEFLOW users. 
It builds on top of the Standard FEFLOW IFM API which provides the elementary functions to access the model data. 
It therefore does not extend the functionality of the IFM in the sense of allowing to do something that was not possible before. 
It rather allows the use of the current functionality in a more productive and more intuitive way, mainly by making common processes available 
to the Data Science tools available in the Python Ecosystem, with (Geo)-Pandas being the most important tool.

The code is free to use, share and modify. 
It is possible to create a private fork and make proprietary modifications.
Users are however encouraged to contribute their own code back to the main branch.

Note: the library is currently in (mature) BETA-status, thus changes may be made that will not be 
backwards compatible.

For a detailed introduction, see [ifm_contrib: An Introduction](./doc/Notebooks/getting_started.ipynb)

## Highlights

**Visualize FEFLOW Results directly in Jupyter**

Create inline plots with the look-and-feel of FEFLOWs directly within Jupyter. The plots can be exported as GeoDataFrames and saved to shape-files easily. *ifm_contrib* adds light support for coordinate systems to FEFLOW.

<img src="doc/Notebooks/highlights_map.png" align="left"> 
<br>
**Process FEFLOWs Time Series with Pandas**

Time Series (aka Power functiosn) and History charts can be easily exported to pandas DataFrames. Automatic conversion to DateTime based on FEFLOWs Reference Time. In-Built Synchronization to observation point reference data.

<img src="doc/Notebooks/highlights_timeseries.png" align="left">
<br>
**Pandas access to Nodal and Elemntal Data, Multi-Layer Wells, and many more**

Read more in [ifm_contrib: An Introduction](./doc/Notebooks/getting_started.ipynb)