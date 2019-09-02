REM coverage check for unittests
REM activate appropriate virtual environment able to run the unittests prior
REM running this script.
REM results are found in ./htmlcov/index.html after execution.

python -m coverage run test_hist_pandas.py
python -m coverage run -a test_hist_pandas.py
python -m coverage run -a test_mesh.py
python -m coverage run -a test_mesh.pyc
python -m coverage run -a test_mesh_geopandas.py
python -m coverage run -a test_mesh_pandas2.py
python -m coverage run -a test_obs_geopandas.py
python -m coverage run -a test_plot.py
python -m coverage run -a test_plot_geopandas.py
python -m coverage run -a test_sel.py
python -m coverage run -a test_simulator.py
python -m coverage run -a test_ts.py
python -m coverage run -a test_ts_pandas.py
python -m coverage html