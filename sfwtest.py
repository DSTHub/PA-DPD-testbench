#manual testset for new clases

import fsw
import instrument
import visa 

#fsw16 = fsw.Fsw(adr = 'TCPIP::localhost::INSTR:')

i = instrument.Inst()
print(i.query("?IDN"))

#rm = visa.ResourceManager('@sim').open_resource('ASRL1::INSTR', read_termination='\n')
print(i.query("?IDN"))
