# PyHT4032L

Hantek 4032L logic analyzer python access. 

## Requirements

* [Python 2.7.x](https://www.python.org)

## Supported drivers

* Hantek original Windows driver
* LibUSB on Windows (requires [Python libusb1 wrapper](https://pypi.org/project/libusb1/) and [libusb-1.0.dll](https://sourceforge.net/projects/libusb/files/libusb-1.0/))
* LibUSB on Linux (requires [Python libusb1 wrapper](https://pypi.org/project/libusb1/) and [libusb-1.0](https://sourceforge.net/projects/libusb/files/libusb-1.0/))

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
- [Hantek 4032L FPGA bitstreams collection](https://nofile.io/f/wHDvptqc84x/la4032_fpga.7z)
