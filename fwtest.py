"""FX2 firmware load example"""
import sys
from HT4032L import loader

la = loader()
print "Using", la.driver.name

la.open()

la.LoadFX2("SpiLoader.bin")

la.close()
