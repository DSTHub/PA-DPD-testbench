# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 13:13:12 2018

@author: d0s
"""
import visa
import instrument


class Smw(instrument.Inst):
    """ Model of R&S SMW generator"""
    
    def __init__(self, addr = 'ASRL1::INSTR', backend = '@sim'):
        """Initialize R&S SMW attributes, try connect via visa
        
        
        :param addr:        str instrument's visa address, like: 'TCPIP0::localhost::inst0::INSTR' or 'ASRL1::INSTR'
        :param backend:     str backend visa library PATH or name
        """

        super().__init__(addr, backend)
 
    def preconfig(self) -> str:
        """
        config self.rem object with SMW param
        
        :return:    str status message
        """

        if self.check_connection:
            self.rem.timeout = 25000
            self.rem.encoding = 'latin_1'
            self.rem.write_termination = None
            self.rem.read_termination = '\n'
			
    def initDPDtestBench(self, alpha, sumRate, cf, reflvl) -> str:     
        """
        Connect to the SMW and
		Configure SMW to use with DPD testbench
        
        :return:    str status message
        """

        if self.check_connection:
			self.write('*cls')
            self.write('abort')
			"""#################CONFIGURE INSTRUMENT#################"""   
            self.write('SOURce1:BB:DM:FORMat APSK32')
            self.write(':SOURce1:BB:DM:SWITching:STATe 1')
            self.write(':SOURce1:BB:DM:APSK32:GAMMa G9D10')
            self.write(':SOURce1:BB:DM:SWITching:STATe 0')
            self.write(':SOURce1:BB:DM:PRBS:LENGth 20')
            self.write(':SOURce1:BB:DM:FILTer:TYPE RCOS')
            self.write(':SOURce1:BB:DM:FILTer:PARameter:RCOSine {}'.format(alpha))
            self.write(':SOURce1:BB:DM:SRATe {}'.format(sumRate))
            self.write(':SOURce1:BB:DM:TRIGger:OUTPut1:ONTime 8')
            self.write(':SOURce1:BB:DM:TRIGger:OUTPut1:OFFTime 1048567')
            self.write(':SOURce1:FREQuency:CW {}'.format(cf))
            self.write(':SOURce1:POWer:POWer {}'.format(reflvl))
            self.write(':SOURce1:BB:DM:STATe 1')
            self.write(':OUTPut1:STATe 1')
            self.write(':SOURce1:INPut:USER3:DIRection OUTP')
            self.write(':OUTPut1:USER3:SIGNal MARKA1')
            return "SMW200A configured"
        else:
            return "Check SMW200A address and reconnect"

