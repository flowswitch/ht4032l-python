"""Firmware service functions access"""
class loader(object):
	def __init__(self, driver):
		self.driver = driver

	def open(self):
		self.driver.open()

	def close(self):
		self.driver.close()

	def WriteMem(self, addr, data):
		"""Write FX2 memory. This request is available regardless of firmware loaded (handled by FX2 USB hardware state machine directly)."""
		res = self.driver.vendor_out(0xA0, addr, 0, data)
		return res!=0

	def load_fx2(self, fname):
		"""Load and start FX2 plain binary firmware image"""
		# reset CPU core
		self.WriteMem(0xE600, "\x01") 
		# load in 0x40 bytes chunks
		hf = open(fname, "rb")
		hf.seek(0, SEEK_END)
		size = hf.tell()
		hf.seek(0)
		addr = 0
		while size:
			chunk_size = min(size, 0x40)
			self.WriteMem(addr, hf.read(chunk_size))
			addr+=chunk_size
			size-=chunk_size
		hf.close()
		# unreset CPU core and start loaded firmware
		self.WriteMem(0xE600, "\x00") 


__all__ = ["loader"]
