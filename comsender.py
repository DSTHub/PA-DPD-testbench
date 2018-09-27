# -*- coding: utf-8 -*-
"""
Created on Thu Sep 27 08:53:21 2018

@author: Stepanov_DI
"""

import instrument

        
class Comsender(instrument.Inst):
    """ Model of R&S FSW spectrum analyzer"""
    
    def __init__(self, addr = 'ASRL1::INSTR', backend = '@sim'):
        """Initialize R&S FSW attributes, try connect via visa
        
        
        :param addr:        str instrument's visa address, like: 'TCPIP0::localhost::inst0::INSTR' or 'ASRL1::INSTR'
        :param backend:     str backend visa library PATH or name
        """

        super().__init__(addr, backend)
 
    def preconfig(self) -> str:
        """
        config self.rem object with FSW param
        
        :return:    str status message
        """

        if self.check_connection:
            self.rem.timeout = 25000
            self.rem.encoding = 'latin_1'
            self.rem.write_termination = None
            self.rem.read_termination = '\n'