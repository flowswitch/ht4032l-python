"""FX2 firmware load example"""
import sys
from HT4032L import HTDriver, loader

la = loader(driver=HTDriver(dump=True))
la.open()

la.LoadFX2("SpiLoader.bin")

la.close()
