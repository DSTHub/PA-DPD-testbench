#Instrument class
#open visa resource 


import visa

class Inst():
    """ Model of R&S FSW spectrum analyzer"""
    
    def __init__(self, addr = 'ASRL1::INSTR', backend = '@sim'): #debug mode, @sim - read pysiva-sim
        """Initialize instrument attributes, try connect via visa
        
        
        :param addr:        str instrument's visa address, like: 'TCPIP0::localhost::inst0::INSTR' or 'ASRL1::INSTR'
        :param backend:     str backend visa library PATH or name
        """

        self.__model = 'None'
        self.__addr = addr
        self.__backend = backend  #Choose Visa backend
        self.__sernum = 'None'
        self.__check_connection = False #Has it remote resource?
        self.connect()

   
    def connect(self) -> str:
        """
        Creating self.rem object for control and read/write data from/to a instrument
        
        :return:    str status message
        """

        try:
            self.rem = visa.ResourceManager(self.__backend).open_resource(self.__addr) #object res by visa

        except AttributeError:
            self.__check_connection = False
            return 'Connection error, address incorrect'

        except:
            self.__check_connection = False
            return 'Connection error, somethink false'

        else:
            self.__check_connection = True
            return 'Connection successes'  
        
        """
        Creating self.visafsw object for control and read data from a R&S FSW
        
        in future will use 
        self.visa.fsw.write('COMMAND')
        self.visa.fsw.read('COMMAND')
        self.visa.fsw.query('COMMAND')
        
        :param fsw_addr:         str visa address FSW analyser, like: 'TCPIP0::localhost::inst0::INSTR' 'ASRL1::INSTR'
        
        """

    def write(self, command:str):   #define write SCPI meth
        if self.__check_connection:
            self.rem.write(command)

    def query(self, command:str):   #define query SCPI meth 
        if self.__check_connection:
            return self.rem.query(command)

    def read(self):   #define query SCPI meth 
        if self.__check_connection:
            return self.rem.read()

    def get_addr(self):
        return self.__addr

    def set_addr(self, addr:str):
        self.__addr = addr

    addr = property(get_addr, set_addr)

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

    def get_check_connection(self):
        return self.__check_connection

    check_connection = property(get_check_connection)

