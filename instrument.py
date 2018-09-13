#Instrument class
#open visa resource 


import visa

class Inst():
    def __init__(self, adr = 'ASRL1::INSTR', backend = '@sim'): #debug mode, @sim - read pysiva-sim
        self.__model = 'None'
        self.__adr = adr
        self.__backend = backend
        self.__sernum = 'None'
        self.rm = visa.ResourceManager(backend).open_resource(adr, read_termination='\n') #object res by visa
   
    def write(self, command):   #define write SCPI meth 
        self.rm.write(command)

    def query(self, command):   #define query SCPI meth 
        self.rm.query(command)
        return self.rm.query(command)
    
    def get_adr(self):
        return self.__adr
    def set_adr(self, adr):
        self.__adr = adr
    adr = property(get_adr, set_adr)
    
    def get_backend(self):
        return self.__backend
    def set_backend(self, backend):
        self.__backend = backend
    backend = property(get_backend, set_backend)

    def get_sernum(self):
        return self.__sernum
    def set_sernum(self, sernum):
        self.__sernum = sernum
    sernum = property(get_sernum, set_sernum)

