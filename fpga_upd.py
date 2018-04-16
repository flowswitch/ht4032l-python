"""FX2 firmware load example"""
from sys import argv, exit
from HT4032L import HTDriver, loader

KnownFlashes = { (0xC2, 0x20, 0x13) : "MX25L4005" }

if len(argv)!=2:
	exit("Usage: "+argv[0]+" <fpga.bin>")

la = loader(driver=HTDriver())
la.open()

print "Loading SPI flash loader..."
la.load_fx2("SpiLoader.bin")

fid = la.GetSpiFlashID()
if fid==(0,0,0):
	la.close()
	exit("Invalid flash ID !")

if not fid in KnownFlashes:
	la.close()
	exit("Unsupported flash ID: %02X, %02X, %02X !" % fid)

print KnownFlashes[fid], "detected"

print "Erasing..."
if not la.EraseSpiFlash():
	la.close()
	exit("Erase failed !")

print "Programming..."
if not la.ProgramSpiFlash(argv[1]):
	la.close()
	exit("Program failed !")

print "Done. Cycle LA power to load new firmware."

la.close()
