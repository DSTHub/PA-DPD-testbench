"""
Fsw class implements SCPI functional
creates the local model of FSW

by pyvisa + NIvisa
For model issue uses backend = '@sim' by pyvisa-sim

@author: Dmitry Stepanov
sep 2018
V2.01

"""
import instrument


class Fsw(instrument.Inst):
    """ This Class is a model of R&S FSW spectrum analyzer"""

    def __init__(self, addr='ASRL1::INSTR', backend='@sim'):
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

    def reconnect(self):
        pass

    def check_connect(self):
        pass

    def ssweep(self) -> str:
        """
        Single sweep (measurement) FSW

        :return:    str status message
        """

        if self.check_connection:
            self.write('INIT')  # сделать однократный запуск
            return "Done 1-sweep FSW"
        else:
            return "Check SFW address and reconnect"

    def savePng(self, work_dir) -> str:
        """
        Save a screenshot in *.PNG

        :param work_dir: Path on FSW to save *.PNG file
        :return:    str status message
        """

        # 'PATH + Filename' -- must be in ''
        print_dir = "'{}.png'".format(work_dir)

        if self.check_connection:
            self.write("HCOP:DEST 'MMEM'")  # Prints the data to a file.")
            # Selects bmp as the file format.")
            self.write("HCOP:DEV:LANG PNG")
            # Selects the file name for the printout.
            self.write("MMEM:NAME {}".format(print_dir))
            self.write("HCOP:ITEM:ALL")  # Prints all screen elements
            # Adds a comment to the printout.
            self.write("HCOP:ITEM:WIND:TEXT '0 dBm power off'")
            # //Stores the printout in a file called 'Screenshot.bmp'.
            self.write("HCOP")
            # FSW.write("HCOP:NEXT") #//Stores the printout in a file called
            # 'Screenshot_001.bmp'.
            return f"spng to {print_dir}"
        else:
            return ("Check SFW address and recconect")

    def saveData(self, work_dir):
        """
        Save a data IQ file *.Dat
        RAW format with Header notation

        :param work_dir: Path on FSW to save *.PNG file
        :return:    str status message
        """

        # 'PATH + Filename' -- must be in ''
        print_dir = "'{}.dat'".format(work_dir)
        if self.check_connection:
            self.write("FORMat:DEXPort:DSEParator POINt")
            self.write("FORMat:DEXPort:HEADer ON")
            self.write("FORMat:DEXPort:MODE RAW")
            self.write("MMEMory:STORe1:TRACe 1, {}".format(print_dir))
            return (f"sdat to {print_dir}")
        else:
            return ("Check SFW address and reconnect")

    def initDPDtestBench(self, cf, reflvl, sumRate, alpha, symLen) -> str:
        """
        Connect to the Fsw and
        Configure Fsw to use with DPD testbench

        :return:    str status message
        """

        if self.check_connection:
            self.write('*rst')
            self.write('*cls')
            self.write('abort')
            # Внешний опорный сигнал 10 МГц
            self.write('ROSCillator:SOURce E10')
            # Create new measurement channel for vector signal analysis named
            # "VSA"
            self.write("INSTrument:CREate DDEM, 'VSA'")
            self.write("INSTrument:SELect 'VSA'")  # выбираем канал VSA
            self.write("SYST:PRES:CHAN:EXEC")  # Делаем пресет канала VSA
            self.write('FREQ:CENT {}'.format(cf))  # Set the center frequency.
            self.write('DISP:TRAC:Y:RLEV {}'.format(
                reflvl))  # Set the reference level
            # --------- Configuring the expected input signal ---------------
            self.write("SENSe:DDEMod:FORMat APSK")  # Set the modulation type
            # Set the modulation order
            self.write("SENSe:DDEMod:APSK:NSTate 32")
            # FSW.write("SENSe:DDEM:MAPP:CAT?") #Query the available symbol
            # mappings for QPSK modulation
            # Set the symbol mapping
            self.write("SENSe:DDEM:MAPP 'DVB_S2_910'")
            self.write("SENSe:DDEM:SRAT {}".format(
                sumRate))  # Set the symbol rate
            # Select the RRC transmit filter
            self.write("SENSe:DDEM:TFIL:NAME 'RRC'")
            self.write("SENSe:DDEM:TFIL:ALPH {}".format(alpha))
            # Переключаем тригер на EXT1
            self.write("TRIGger:SEQuence:SOURce EXTernal")
            self.write("INIT:CONT OFF")  # switch to single sweep mode
          # //Initiate a basic frequency sweep and wait until the sweep has finished.
            # захватываемое колличество символов
            self.write("DDEMod:RLENgth:VALue {} SYM".format(symLen))
            # колличество символов, отобр на экране
            self.write('DDEMod:TIME {}'.format(symLen))
            return ("FSW configured")
        else:
            return("No FSW connection!")
