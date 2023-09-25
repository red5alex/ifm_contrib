import pytest

import ifm_contrib as ifm


@pytest.fixture(autouse=True)
def change_test_dir(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)


@pytest.fixture(autouse=True)
def set_feflow_license():
    ifm.forceLicense("Viewer")
