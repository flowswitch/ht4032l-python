"""FX2 firmware load example"""
import sys
from HT4032L import HTDriver, loader

la = loader(driver=HTDriver())
la.open()

la.load("ahz.bin")

la.close()
