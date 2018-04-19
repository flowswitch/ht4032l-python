"""Firmware service functions access"""
from os.path import getsize
from Driver import GetDevice

try:
	from progressbar import ProgressBar
except ImportError:
	class ProgressBar:
		"""ProgressBar stub. Do pip install progressbar instead."""
		def __init__(self, maxval):
			pass
		def start(self):
			return self
		def update(self, val):
			pass
		def finish(self):
			pass


class loader(object):
	"""fw/eep/flash loader"""
	def __init__(self, driver="auto", index=0, dump=False):
		"""Param: driver - driver wrapper instance"""
		if driver=="auto":
			self.driver = GetDevice(index=index, dump=dump)
			if not self.driver:
				raise Exception("Device not found")
		else:
			self.driver = driver

	def open(self):
		self.driver.open()

	def close(self):
		self.driver.close()

	########### FX2 loader ######################################

	def WriteMem(self, addr, data):
		"""Write FX2 memory. This request is available regardless of firmware loaded (handled by FX2 USB hardware state machine directly)."""
		res = self.driver.vendor_out(0xA0, addr, 0, data)
		return res!=0

	def LoadFX2(self, fname):
		"""Load and start FX2 plain binary firmware image"""
		# reset CPU core
		self.WriteMem(0xE600, "\x01") 
		# load in 0x40 bytes chunks
		size = getsize(fname)
		hf = open(fname, "rb")
		pb = ProgressBar(maxval=size).start()
		addr = 0
		while size:
			pb.update(addr)
			chunk_size = min(size, 0x40)
			self.WriteMem(addr, hf.read(chunk_size))
			addr+=chunk_size
			size-=chunk_size
		pb.finish()
		hf.close()
		# unreset CPU core and start loaded firmware
		self.WriteMem(0xE600, "\x00") 

	########## FPGA flash access ################################

	def ReadSpiFlash(self, addr, size):
		"""Read SPI (FPGA) flash. Requires running SpiLoader"""
		return self.driver.vendor_in(0xA2, addr & 0x0FFFF, addr>>16, size)

	def WriteSpiFlash(self, addr, data):
		"""Write SPI (FPGA) flash. Requires running SpiLoader"""
		return self.driver.vendor_out(0xA2, addr & 0x0FFFF, addr>>16, data)!=0

	def EraseSpiFlash(self):
		"""Erase SPI (FPGA) flash. Requires running SpiLoader"""
		return self.driver.vendor_in(0xA9, 0, 0, 1)=="\x00"

	def GetSpiFlashID(self):
		"""Read SPI (FPGA) flash ID. Requires running SpiLoader"""
		res = self.driver.vendor_in(0xA5, 0, 0, 3)
		if len(res)!=3:
			return (0, 0, 0)
		else:
			return ord(res[0]), ord(res[1]), ord(res[2])

	def ProgramSpiFlash(self, fname):
		"""Write a file to SPI (FPGA) flash. Requires running SpiLoader"""
		# write in 0x100 bytes chunks
		size = getsize(fname)
		hf = open(fname, "rb")
		pb = ProgressBar(maxval=size).start()
		addr = 0
		while size:
			pb.update(addr)
			chunk_size = min(size, 0x100)
			if not self.WriteSpiFlash(addr, hf.read(chunk_size)+"\xFF"*(0x100-chunk_size)):
				pb.finish()
				hf.close()
				print "Write failed at %X !" % (addr)
				return False
			addr+=chunk_size
			size-=chunk_size
		pb.finish()
		hf.close()
		return True

	def DumpSpiFlash(self, fname, size):
		"""Read SPI (FPGA) flash to file. Requires running SpiLoader"""
		hf = open(fname, "wb")
		pb = ProgressBar(maxval=size).start()
		addr = 0
		while size:
			pb.update(addr)
			chunk_size = min(size, 0x100)
			data = self.ReadSpiFlash(addr, chunk_size)
			if data=="":
				pb.finish()
				hf.close()
				print "Read failed at %X !" % (addr)
				return False
			hf.write(data)
			addr+=chunk_size
			size-=chunk_size
		pb.finish()
		hf.close()
		return True
				

__all__ = ["loader"]
