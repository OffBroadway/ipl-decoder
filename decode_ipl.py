import sys
import platform

plat = platform.uname()
system = plat.system
if system == "Windows":
    sys.path.append('.')

from gcn.dol import *
from ext.descrambler import Descrambler

dol = DOL()

dol.bss_address = 0
dol.bss_size = 0
dol.entry_point_address = 0x81300000

filename = "ipl.bin"
if len(sys.argv) > 1:
    filename = sys.argv[1]

with open(filename, 'rb') as f:
    data = f.read()

descrambler = Descrambler()
ipl = descrambler.get_code(data)

with open('dec-ipl.bin', 'wb') as f:
    f.write(ipl)

header_size = 0x100
ipl_size = len(ipl)

dol.data.write(b'\x00' * header_size)
dol.data.write(ipl)

dol.sections = [
    DOLSection(header_size, dol.entry_point_address, ipl_size)
]

dol.save_changes()

with open('dec-ipl.dol', 'wb') as f:
    buf = dol.data.getvalue()
    f.write(buf)
