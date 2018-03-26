class loader(object):
	def __init__(self, driver):
		self.driver = driver

	def open(self):
		self.driver.open()

	def close(self):
		self.driver.close()

	def WriteMem(self, addr, data):
		res = self.driver.vendor_out(0xA0, addr, 0, data)
		return res!=0

	def load(self, fname):
		#hf = open(fname, "rb")
		self.WriteMem(0xE600, "\x01") # reset 8051
		#TODO: load at 0 in [0x40] chunks 
		self.WriteMem(0, "\x02")

		self.WriteMem(0xE600, "\x00") # unreset 8051

__all__ = ["loader"]
