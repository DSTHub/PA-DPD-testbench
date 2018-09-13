#9:50 11.09.2018

import visa 

class Fsw():
    def __init__(self, adr = 'ASRL1::INSTR', backend = '@sim') :
        self.adr = adr
        self.backend = backend
        self.__cf = 0
        self.__reflvl = 0
        self.rm = visa.ResourceManager(backend).open_resource(adr, read_termination='\n')

    def write(self, command):
        self.rm.write(command)

    def query(self, command):
        self.rm.query(command)
        return self.rm.query(command)
    
        


 















