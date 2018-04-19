"""Guess the driver kind"""
import os
from LibusbDriver import LibusbDriver

def GetDevice(index=0, dump=False):
	drv = LibusbDriver(index=index, dump=dump)
	try:
		drv.open()
		drv.close()
		return drv
	except:
		if os.name=="nt":
			from HTDriver import HTDriver
			drv = HTDriver(index=index, dump=dump)
			try:
				drv.open()
				drv.close()
				return drv
			except:
				return None

__all__ = ["GetDevice"]
