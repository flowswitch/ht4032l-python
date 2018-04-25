"""Guess the driver kind"""

def GetDevice(index=0, dump=False):
	try:
		print "Probing LibUSB...",
		from LibusbDriver import LibusbDriver
		drv = LibusbDriver(index=index, dump=dump)
		drv.open()
		drv.close()
		print "ok"
		return drv
	except Exception, e:
		print e
		try:
			print "Probing Hantek...",
			from HTDriver import HTDriver
			drv = HTDriver(index=index, dump=dump)
			drv.open()
			drv.close()
			print "ok"
			return drv
		except Exception, e:
			print e
			return None

__all__ = ["GetDevice"]
