"""Guess the driver kind"""

def GetDevice(index=0, dump=False):
	try:
		from LibusbDriver import LibusbDriver
		drv = LibusbDriver(index=index, dump=dump)
		drv.open()
		drv.close()
		return drv
	except:
		try:
			from HTDriver import HTDriver
			drv = HTDriver(index=index, dump=dump)
			drv.open()
			drv.close()
			return drv
		except:
			return None

__all__ = ["GetDevice"]
