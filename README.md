# PyHT4032L

Hantek 4032L logic analyzer python access. 

## Supported drivers

* Hantek original Windows driver

## FPGA flash tools

* fpga_get_ver: get current FPGA version
* fpga_dump: dump FPGA bitstream to file
* fpga_upd: update FPGA bitstream from file

## Known FPGA versions

* V0 found in LAs from years around 2013. Doesn't support external clocking. Bug: slowdowns at low sample rates. Bug: all-zero IN packets before first STATUS/DATA packet.
* V4303 from 29 Apr 2015. Supports external clocking, both bugs of V0 listed above are fixed.
* V4304 from 2 Mar 2018. No visible differences from V4303

## See also

- [Protocol description on Sigrok site](https://sigrok.org/wiki/Hantek_4032L)
- [FPGA loader sources](https://github.com/andy9a9/fx2eeprom/tree/master/fx2eeprom/FX2)
