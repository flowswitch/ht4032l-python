import sys
import ctypes
from time import sleep
from array import array

cmd_start = "\x7F\x01\x1F\x08\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\x00\x00\x00\x00\x02\x00\x64\x00\x00\x00\xE8\x03\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\xFF\xFF\x00\x00\x00\x00\x02\x00\x64\x00\x00\x00\xE8\x03\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\x1A\x2B"
cmd_poll  = "\x7F\x01\x1F\x0A\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x30\x1F\x00\x00\xFF\xFF\x00\x00\x00\x00\x02\x00\x64\x00\x00\x00\xE8\x03\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\x30\x3F\x00\x00\xFF\xFF\x00\x00\x00\x00\x02\x00\x64\x00\x00\x00\xE8\x03\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\x3A\x4B"
cmd_get   = "\x7F\x01\x1F\x0A\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x30\x1F\x00\x00\xFF\xFF\x00\x00\x00\x00\x02\x00\x64\x00\x00\x00\xE8\x03\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\x30\x3F\x00\x00\xFF\xFF\x00\x00\x00\x00\x02\x00\x64\x00\x00\x00\xE8\x03\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\x5A\x6B"

##############################################################################################

class Trigger(ctypes.LittleEndianStructure):
	_pack_ = 1
	_fields_ = [("EdgeSignal", ctypes.c_ulong, 5),
				("EdgeType", ctypes.c_ulong, 2),
				("_unused7", ctypes.c_ulong, 1),
				("DataRangeType", ctypes.c_ulong, 2),
				("TimeRangeType", ctypes.c_ulong, 2),
				("DataRangeEnable", ctypes.c_ulong, 1),
				("TimeRangeEnable", ctypes.c_ulong, 1),
				("_unused14", ctypes.c_ulong, 2),
				("CombinedDataSel", ctypes.c_ulong, 2),
				("CombinedEnable", ctypes.c_ulong, 1),
				("_unused19", ctypes.c_ulong, 13),
				("DataRangeMin", ctypes.c_ulong),
				("DataRangeMax", ctypes.c_ulong),
				("TimeRangeMin", ctypes.c_ulong),
				("TimeRangeMax", ctypes.c_ulong),
				("DataRangeMask", ctypes.c_ulong),
				("CombinedMask", ctypes.c_ulong),
				("CombinedData", ctypes.c_ulong)]

class Config(ctypes.LittleEndianStructure):
	_pack_ = 1
	_fields_ = [("Magic", ctypes.c_ushort),
				("SampleRate", ctypes.c_ubyte),
				("EnableTrigger1", ctypes.c_ubyte, 1),
				("EnableTrigger2", ctypes.c_ubyte, 1),
				("TriggerAnd", ctypes.c_ubyte, 1),
				("UsbxiTrig0", ctypes.c_ubyte, 1),
				("UsbxiTrig1", ctypes.c_ubyte, 1),
				("_unused5", ctypes.c_ubyte, 2),
				("UsbxiCheckMode", ctypes.c_ubyte, 1),
				("DacA", ctypes.c_ushort),
				("DacB", ctypes.c_ushort),
				("UsbxiData", ctypes.c_ubyte),
				("_unused0", ctypes.c_ubyte),
				("SampleDepth", ctypes.c_ulong),
				("PretriggerDepth", ctypes.c_ulong),
				("Trigger1", Trigger),
				("Trigger2", Trigger),
				("Command", ctypes.c_ushort)]

PARAMS_MAGIC = 0x017F
STATUS_MAGIC = 0x2B1A037F
DATA_MAGIC = 0x2B1A027F
DATA_END = 0x4D3C037F

CMD_START = 0x2B1A
CMD_GET_STATUS = 0x4B3A
CMD_GET_DATA = 0x6B5A
CMD_USBXI_ERASER_DATA = 0xAB9A
CMD_USBXI_SET_SYNC_TRIG_OUT = 0xCBBA

############################################################################################

def _thr2dac(voltage):
	voltage = max(-6.0, voltage)
	voltage = min(6.0, voltage)
	vref = 1.8-voltage
	vref = max(-5.0, vref)
	vref = min(10.0, vref)
	dac = min(4095, int(round((vref+5.0)*4096.0/15.0)))
	return dac

############################################################################################

class LA(object):
	def __init__(self, driver):
		self.driver = driver
		self.config = Config()
		ctypes.memmove(ctypes.addressof(self.config), cmd_start, ctypes.sizeof(self.config))
		self.status = array('L', "\x00"*1024)

	def open(self):
		self.driver.open()

	def close(self):
		self.driver.close()
		
	def Reset(self):
		res = self.driver.vendor_out(0xB3, 0, 0, "\x0F\x03\x03\x03\x00\x00\x00\x00\x00\x00")
		sleep(0.005)
		return res!=0

	def Start(self):
		self.driver.write(buffer(self.config)[:])

	def Poll(self):
		self.driver.write(cmd_poll)
		outsize = 0
		got_start = False
		retry_count = 0
		while retry_count<5 and outsize<0x100:
			data = self.driver.read(0x200)
			if not len(data):
				retry_count += 1
				continue
			retry_count = 0
			chunk = array('L', data)
			for val in chunk:
				if got_start:
					if val==DATA_END:
						break
				else:
					if val==STATUS_MAGIC:
						got_start = True										
				if got_start:
					self.status[outsize] = val
					outsize += 1
		return retry_count<5

	def GetData(self):
		self.driver.write(cmd_get)
		outbuf = array('L')
		outsize = 0
		got_start = False
		retry_count = 0
		while retry_count<5 and outsize<self.config.SampleDepth:
			data = self.driver.read(0x200)
			if not len(data):
				retry_count += 1
				continue
			retry_count = 0
			chunk = array('L', data)
			for val in chunk:
				if got_start:
					if val==DATA_END:
						break
					outbuf.append(val)
					outsize += 1
				else:
					if val==DATA_MAGIC:
						got_start = True										
		return outbuf

	def GetTriggerStatus(self):
		if not self.Poll():
			return -1
		return self.status[2]

	def GetBusData(self):
		if not self.Poll():
			return -1
		return self.status[1]

	def SetThresholdA(self, voltage):
		self.config.DacA = _thr2dac(voltage)

	def SetThresholdB(self, voltage):
		self.config.DacB = _thr2dac(voltage)

__all__ = ["LA"]
