"""Acquisition example"""
import sys
from HT4032L import LA

la = LA()
print "Using", la.driver.name

la.open()

print "Reset..."
la.Reset()

print "FPGA version: %X" % la.GetFpgaVersion()

la.close()
