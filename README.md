# ifm_contrib

**Note that ifm_contrib is at the moment OUT OF MAINTENANCE. DHI does not guarantee its correct functioning or compatibility with FEFLOW Versions >= 8.0. 
DHI might investigate in the future the possibility of finding an alternative solution for such library.**

**ifm_contrib** is an Open-Source Extension of the IFM, the Python API of FEFLOW.

It is **written by FEFLOW users, for FEFLOW users**. It builds on top of the Standard FEFLOW IFM API which provides the elementary functions to access the model data. 
It therefore does not extend the functionality of the IFM in the sense of allowing to do something that was not possible before. 
It rather allows the use of the current functionality in a more productive and more intuitive way, mainly by making common processes available 
to the Data Science tools available in the Python Ecosystem, with (Geo)-Pandas being the most important tool.

The code is free to use, share and modify. 
It is possible to create a private fork and make proprietary modifications.
Users are however encouraged to contribute their own code back to the main branch.

Note: the library is currently in (mature) BETA-status, thus changes may be made that will not be 
backwards compatible.

**For a detailed introduction and installation notes, see [ifm_contrib: An Introduction](./doc/Notebooks/getting_started.ipynb)**

## Highlights

### Visualize FEFLOW Results directly in Jupyter

Create inline plots with the look-and-feel of FEFLOWs directly within Jupyter. The plots can be exported as GeoDataFrames and saved to shape-files easily. \
*ifm_contrib* adds light support for coordinate systems to FEFLOW.

<img src="doc/Notebooks/highlights_map.png"> 

### Process FEFLOWs Time Series with Pandas

Time Series (aka Power functiosn) and History charts can be easily exported to pandas DataFrames. Automatic conversion to DateTime based on FEFLOWs Reference Time. In-Built Synchronization to observation point reference data.

<img src="doc/Notebooks/highlights_timeseries.png">

### Pandas-access to Nodal and Elemntal Data, Multi-Layer Wells, and much more..

Read more in [ifm_contrib: An Introduction](./doc/Notebooks/getting_started.ipynb)
