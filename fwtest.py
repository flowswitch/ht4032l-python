import sys
from HT4032L import HTDriver, loader
from util import outhex

la = loader(driver=HTDriver())
la.open()

la.load("ahz")

la.close()
