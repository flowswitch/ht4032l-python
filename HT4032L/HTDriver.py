"""Hantek Windows driver wrapper"""
from DriverTypes import DriverNotSupportedException
import os
if os.name!="nt":
	raise DriverNotSupportedException("Not a Windows platform")

import ctypes
import ctypes.wintypes as wintypes
from ctypes import windll
from struct import pack, unpack
from binascii import hexlify

LPDWORD = ctypes.POINTER(wintypes.DWORD)
LPOVERLAPPED = wintypes.LPVOID
LPSECURITY_ATTRIBUTES = wintypes.LPVOID

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
GENERIC_EXECUTE = 0x20000000
GENERIC_ALL = 0x10000000

CREATE_NEW = 1
CREATE_ALWAYS = 2
OPEN_EXISTING = 3
OPEN_ALWAYS = 4
TRUNCATE_EXISTING = 5

FILE_ATTRIBUTE_NORMAL = 0x00000080

INVALID_HANDLE_VALUE = -1

NULL = 0
FALSE = wintypes.BOOL(0)
TRUE = wintypes.BOOL(1)


def _CreateFile(filename, access, mode, creation, flags):
	"""See: CreateFile function

	http://msdn.microsoft.com/en-us/library/windows/desktop/aa363858(v=vs.85).aspx

	"""
	CreateFile_Fn = windll.kernel32.CreateFileW
	CreateFile_Fn.argtypes = [
			wintypes.LPWSTR,					# _In_		  LPCTSTR lpFileName
			wintypes.DWORD,					 # _In_		  DWORD dwDesiredAccess
			wintypes.DWORD,					 # _In_		  DWORD dwShareMode
			LPSECURITY_ATTRIBUTES,			  # _In_opt_	  LPSECURITY_ATTRIBUTES lpSecurityAttributes
			wintypes.DWORD,					 # _In_		  DWORD dwCreationDisposition
			wintypes.DWORD,					 # _In_		  DWORD dwFlagsAndAttributes
			wintypes.HANDLE]					# _In_opt_	  HANDLE hTemplateFile
	CreateFile_Fn.restype = wintypes.HANDLE

	return wintypes.HANDLE(CreateFile_Fn(filename,
						 access,
						 mode,
						 NULL,
						 creation,
						 flags,
						 NULL))


def _DeviceIoControl(devhandle, ioctl, inbuf, inbufsiz, outbuf, outbufsiz):
	"""See: DeviceIoControl function

	http://msdn.microsoft.com/en-us/library/aa363216(v=vs.85).aspx

	"""
	DeviceIoControl_Fn = windll.kernel32.DeviceIoControl
	DeviceIoControl_Fn.argtypes = [
			wintypes.HANDLE,					# _In_		  HANDLE hDevice
			wintypes.DWORD,					 # _In_		  DWORD dwIoControlCode
			wintypes.LPVOID,					# _In_opt_	  LPVOID lpInBuffer
			wintypes.DWORD,					 # _In_		  DWORD nInBufferSize
			wintypes.LPVOID,					# _Out_opt_	 LPVOID lpOutBuffer
			wintypes.DWORD,					 # _In_		  DWORD nOutBufferSize
			LPDWORD,							# _Out_opt_	 LPDWORD lpBytesReturned
			LPOVERLAPPED]					   # _Inout_opt_   LPOVERLAPPED lpOverlapped
	DeviceIoControl_Fn.restype = wintypes.BOOL

	# allocate a DWORD, and take its reference
	dwBytesReturned = wintypes.DWORD(0)
	lpBytesReturned = ctypes.byref(dwBytesReturned)

	status = DeviceIoControl_Fn(devhandle,
				  ioctl,
				  inbuf,
				  inbufsiz,
				  outbuf,
				  outbufsiz,
				  lpBytesReturned,
				  None)

	return status, dwBytesReturned.value
	
############################################################################################

HT_IOCTL_READ   = 0x22204E
HT_IOCTL_WRITE  = 0x222051
HT_IOCTL_VENDOR = 0x222059

class HTDriver(object):
	"""Wrapper class"""
	def __init__(self, index=0, dump=False):
		"""Params:
		index - device index
		dump - dump all communications
		"""
		self.name = "Hantek Windows driver"
		self.index = index
		self.dump = dump
		self._fhandle = None

	def open(self):
		"""Open device"""
		if self._fhandle:
			return
		self._fhandle = _CreateFile(
				"\\\\.\\d4032-%d" % (self.index),
				GENERIC_READ | GENERIC_WRITE,
				0,
				OPEN_EXISTING,
				FILE_ATTRIBUTE_NORMAL)
		self._validate_handle()

	def close(self):
		"""Close device"""
		if self._fhandle:
			windll.kernel32.CloseHandle(self._fhandle)
			self._fhandle = None
		
	def _validate_handle(self):
		if self._fhandle is None:
			raise Exception('No file handle')
		if self._fhandle.value == wintypes.HANDLE(INVALID_HANDLE_VALUE).value:
			self._fhandle = None
			raise Exception('Failed to open device %d. GetLastError(): %d' %
					(self.index, windll.kernel32.GetLastError()))

	def _ioctl(self, ctl, inbuf, inbufsiz, outbuf, outbufsiz):
		self._validate_handle()
		return _DeviceIoControl(self._fhandle, ctl, inbuf, inbufsiz, outbuf, outbufsiz)

	def read(self, size):
		"""Read from IN pipe"""
		buf = ctypes.create_string_buffer(size)
		sts, outsize = self._ioctl(HT_IOCTL_READ, "\x01\x00\x00\x00", 4, ctypes.byref(buf), size)
		if not sts:
			return ""
		rsp = buf.raw[0:outsize]
		if self.dump:
			print "<", hexlify(rsp)
		return rsp

	def write(self, data):
		"""Write to OUT pipe"""
		if self.dump:
			print ">", hexlify(data)
		sts, outsize = self._ioctl(HT_IOCTL_WRITE, "\x00\x00\x00\x00", 4, data, len(data))
		if not sts:
			return 0
		return outsize
					 
	def vendor_out(self, request, value, index, data):
		"""EP0 vendor out"""
		if self.dump:
			print "%02X %04X %04X >" % (request, value, index), hexlify(data)
		sts, outsize = self._ioctl(HT_IOCTL_VENDOR, pack("<BHBBBHH", 0, 2, 0, request, 0, value, index), 10, data, len(data))
		if not sts:
			return 0
		return outsize

	def vendor_in(self, request, value, index, length):
		"""EP0 vendor in"""
		buf = ctypes.create_string_buffer(length)
		sts, outsize = self._ioctl(HT_IOCTL_VENDOR, pack("<BHBBBHH", 1, 2, 0, request, 0, value, index), 10, ctypes.byref(buf), length)
		if not sts:
			return ""
		rsp = buf.raw[0:outsize]
		if self.dump:
			print "%02X %04X %04X <" % (request, value, index), hexlify(rsp)
		return rsp


__all__ = ["HTDriver"]
