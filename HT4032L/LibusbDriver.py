"""LibUSB driver wrapper"""
# Requires libusb1 package. See https://pypi.org/project/libusb1
import usb1
from struct import pack, unpack
from binascii import hexlify

HT4032L_IFACE  = 0
HT4032L_EP_IN  = 0x86
HT4032L_EP_OUT = 0x02

class LibusbDriver(object):
	"""Wrapper class"""
	def __init__(self, index=0, dump=False):
		"""Params:
		index - device index
		dump - dump all communications
		"""
		self.name = "LibUSB driver"
		self.index = index
		self.dump = dump
		self._fhandle = None

	def open(self):
		"""Open device"""
		if self._fhandle:
			return
		self._ctx = usb1.USBContext()
		self._fhandle = self._ctx.openByVendorIDAndProductID(0x04B5, 0x4032, skip_on_error=True)
		if not self._fhandle:
			raise Exception("Failed to open device !")
		self._fhandle.claimInterface(HT4032L_IFACE)

	def close(self):
		"""Close device"""
		if self._fhandle:
			self._fhandle.releaseInterface(HT4032L_IFACE)
			self._fhandle = None
			self._ctx = None
		
	def read(self, size):
		"""Read from IN pipe"""
		if self.dump:
			print "<",
		data = self._fhandle.bulkRead(HT4032L_EP_IN, size)
		if not data:
			if self.dump:
				print "NG"
			return ""
		data = "".join(map(chr, data))
		if self.dump:
			print "[%X]" % (len(data)), hexlify(data)
		return data

	def write(self, data):
		"""Write to OUT pipe"""
		if self.dump:
			print "> [%X]" % (len(data)), hexlify(data)
		return self._fhandle.bulkWrite(HT4032L_EP_OUT, data)
					 
	def vendor_out(self, request, value, index, data):
		"""EP0 vendor out"""
		if self.dump:
			print "%02X %04X %04X >" % (request, value, index), hexlify(data)
		return self._fhandle.controlWrite(0x40, request, value, index, data)

	def vendor_in(self, request, value, index, length):
		"""EP0 vendor in"""
		if self.dump:
			print "%02X %04X %04X <" % (request, value, index),
		data = self._fhandle.controlRead(0x40, request, value, index, length)
		if not data:
			if self.dump:
				print "NG"
			return ""
		data = "".join(map(chr, data))
		if self.dump:
			print "[%X]" % (len(data)), hexlify(data)
		return data


__all__ = ["LibusbDriver"]
