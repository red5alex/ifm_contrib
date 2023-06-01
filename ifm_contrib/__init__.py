# -*- coding: UTF-8 -*-


# ONLY EDIT THIS FILE IF YOU KNOW WHAT YOU DO!

import sys
import os
import platform

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
        if 'FEFLOW72_ROOT' in os.environ:
            feflow_root = os.environ['FEFLOW72_ROOT']
        if 'FEFLOW73_ROOT' in os.environ:
            feflow_root = os.environ['FEFLOW73_ROOT']
        if 'FEFLOW74_ROOT' in os.environ:
            feflow_root = os.environ['FEFLOW74_ROOT']
        if 'FEFLOW75_ROOT' in os.environ:
            feflow_root = os.environ['FEFLOW75_ROOT']
        if 'FEFLOW80_ROOT' in os.environ:
            feflow_root = os.environ['FEFLOW80_ROOT']

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
    if sys.version_info >= (3, 11) and sys.version_info < (3, 12):
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
            import warnings
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
