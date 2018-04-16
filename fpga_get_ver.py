"""Acquisition example"""
import sys
from HT4032L import HTDriver, LA

la = LA(driver=HTDriver()) # use Hantek native driver
la.open()

print "Reset..."
la.Reset()

print "FPGA version: %X" % la.GetFpgaVersion()

la.close()
