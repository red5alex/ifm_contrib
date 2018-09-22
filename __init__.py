#-*- coding: UTF-8 -*-

def _():
	import sys, os
	if 'FEFLOW72_ROOT' in os.environ:
		feflow_root = os.environ['FEFLOW72_ROOT']
		sys.path.append(feflow_root+'bin64')
#		if sys.version_info > (3, 0):
#			sys.path.append(feflow_root+'python/pyscriptlib37.zip')
#		else:
#			sys.path.append(feflow_root+'python/pyscriptlib27.zip')
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
elif sys.version_info >= (3, 7) and sys.version_info < (3, 8):
	from ifm37 import *
elif sys.version_info >= (3, 6) and sys.version_info < (3, 7):
	from ifm36 import *
elif sys.version_info >= (3, 5) and sys.version_info < (3, 6):
	from ifm35 import *
elif sys.version_info >= (2, 7) and sys.version_info < (2, 8):
	from ifm27 import *
else:
	raise ImportError('This python version is not supported by FEFLOW!')
