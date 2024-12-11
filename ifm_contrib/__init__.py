# -*- coding: UTF-8 -*-


# ONLY EDIT THIS FILE IF YOU KNOW WHAT YOU DO!

import sys
import os
import platform
import warnings
import re

def _():
    global feflow_root
    feflow_root = None

    # check if a FEFLOW Kernel version is specified.
    if 'FEFLOW_KERNEL_VERSION' in os.environ:
        kernel_version = os.environ['FEFLOW_KERNEL_VERSION']
        root_env_variable = 'FEFLOW{}_ROOT'.format(str(kernel_version))

        # set feflow root folder if FEFLOWxx_ROOT exists, otherwise error
        if root_env_variable in os.environ:
            feflow_root = os.environ[root_env_variable]
        else:
            raise EnvironmentError("Environment variable FEFLOW_KERNEL_VERSION is set to {}, but {} is missing. Is "
                                   "FEFLOW installed?".format(kernel_version, root_env_variable))

    # use highest available version if not specified
    else:
        feflow_roots = [env_var for env_var in os.environ if "FEFLOW" in env_var and "ROOT" in env_var]
        if len(feflow_roots) == 0:
            raise ImportError("The environmental variable for the FEFLOW installation could not be found. Either it needs to be set manually or FEFLOW is not installed.")
        elif "FEFLOW_ACTIVE_ROOT" in os.environ:
            warnings.warn("If you choose 'FEFLOW_ACTIVE_ROOT', the 'LD_LIBRARY_PATH' must be assigned to the correct FEFLOW version.")
            feflow_root = os.environ["FEFLOW_ACTIVE_ROOT"]
        elif len(feflow_roots) >= 1:
            if len(feflow_roots) > 1:
                warn_message = """
                               There is more than 1 FEFLOW installation. 
                               The latest one was chosen for the API. If another one is to be configured, 
                               the environmental variable 'FEFLOW_ACTIVE_ROOT' needs to be set to the corresponding path, 
                               as well as the corresponding 'LD_LIBRARY_PATH'. 
                               In Linux: 'export FEFLOW_ACTIVE_ROOT=/opt/feflow/X, with X the version.
                               """
                warnings.warn(warn_message)
            digits = []
            for root in feflow_roots:
                m = re.search(r"FEFLOW(\d{2,3})_ROOT",root)
                digits.append(int(m.group(1)))
            digits.sort()
            feflow_root = os.environ[f"FEFLOW{digits[-1]}_ROOT"]

    if feflow_root is not None:
        if platform.system() == 'Windows':
            sys.path.append(feflow_root + 'bin64')
        else:
            sys.path.append(feflow_root + '/lib64')
    else:
        print('The FEFLOW installation could not be found')
        
    if sys.platform == 'cli':
        import clr
        clr.AddReference('IronPython.Feflow72')

_()
del _

import sys

if sys.platform == 'cli':
    from feflow import *


    def loadDocument(f):
        return PyFeflowKernel.loadDocument(f)


    def forceLicense(l):
        return PyFeflowKernel.forceLicense(l)
else:
    if sys.version_info >= (3, 12) and sys.version_info < (3, 13):
        from ifm312 import *
        from ifm312 import loadDocument as _loadDocument
    elif sys.version_info >= (3, 11) and sys.version_info < (3, 12):
        from ifm311 import *
        from ifm311 import loadDocument as _loadDocument
    elif sys.version_info >= (3, 10) and sys.version_info < (3, 11):
        from ifm310 import *
        from ifm310 import loadDocument as _loadDocument
    elif sys.version_info >= (3, 9) and sys.version_info < (3, 10):
        from ifm39 import *
        from ifm39 import loadDocument as _loadDocument
    elif sys.version_info >= (3, 8) and sys.version_info < (3, 9):
        from ifm38 import *
        from ifm38 import loadDocument as _loadDocument
    elif sys.version_info >= (3, 7) and sys.version_info < (3, 8):
        from ifm37 import *
        from ifm37 import loadDocument as _loadDocument
    elif sys.version_info >= (3, 6) and sys.version_info < (3, 7):
        from ifm36 import *
        from ifm36 import loadDocument as _loadDocument
    elif sys.version_info >= (3, 5) and sys.version_info < (3, 6):
        from ifm35 import *
        from ifm35 import loadDocument as _loadDocument
    elif sys.version_info >= (2, 7) and sys.version_info < (2, 8):
        from ifm27 import *
        from ifm27 import loadDocument as _loadDocument
    else:
        raise ImportError(f'This python version is not supported by FEFLOW!\n{sys.version_info}')

    from . import colormaps

    from . import c

    def loadDocument(f, import_ifm_attribs=True, ifm_classic=None, crs=None, close_others=False):
        """
        This replaces the original ifm.loadDocument function.
        it returns a copy of an IFM Document including the ifm_contrib extension.
        :param f: filename of fem or dac
        :param import_ifm_attribs: If False (default), do not import classic ifm calls.
        Use this function to prevent Kernel crashes.
        :param crs: set the models coordinate system (Proj4 string)
        :return: doctype including ifm_contrib extension
        """

        if close_others:
            c.closeAllDocuments()

        if ifm_classic is not None:
            warnings.warn(DeprecationWarning("ifm_classic is depreciated, use import_ifm_attribs!"))
            import_ifm_attribs = ifm_classic

        return doc_contrib(f, import_ifm_attribs=import_ifm_attribs, crs=crs)


    class doc_contrib:
        """
        Contributors IfmDocument class.
        This class loads the original IfmDocument class and adds the contributors methods.
        """

        def __init__(self, filename, import_ifm_attribs=True, crs=None):
            # load document as standard IFM object
            self.pdoc = _loadDocument(filename)

            # transfer all attributes to contributors IFM object
            if import_ifm_attribs:
                for item in dir(self.pdoc):
                    if item == "handle":
                        continue

                    self.__dict__[item] = self.pdoc.__getattribute__(item)

            # import contributors library
            from . import contrib_lib
            self.c = contrib_lib.IfmContrib(self)

            # add original filename
            self.c.original_filename = filename

            # add coordinate system
            if crs is not None:
                self.c.crs = crs


        def __getattr__(self, item):
            # if an unknown attribute called, check if doc.pdoc has the atrribute and use it if so.
            # required for code compatibility with classic IFM if ifm_classic parameter is set to False.
            return self.pdoc.__getattribute__(item)
