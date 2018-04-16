"""FX2 firmware load example"""
from sys import argv, exit
from HT4032L import HTDriver, loader

KnownFlashes = { (0xC2, 0x20, 0x13) : ("MX25L4005", 0x80000) }

if len(argv)!=2:
	exit("Usage: "+argv[0]+" <outfile.bin>")

la = loader(driver=HTDriver())
la.open()

print "Loading SPI flash loader..."
la.LoadFX2("SpiLoader.bin")

fid = la.GetSpiFlashID()
if fid==(0,0,0):
	la.close()
	exit("Invalid flash ID !")

if not fid in KnownFlashes:
	la.close()
	exit("Unsupported flash ID: %02X, %02X, %02X !" % fid)

print "%s detected, size: %X" % KnownFlashes[fid]

print "Reading..."
if not la.DumpSpiFlash(argv[1], KnownFlashes[fid][1]):
	la.close()
	exit("Read failed !")

print "Done. Cycle LA power to return to normal mode."

la.close()
