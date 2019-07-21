"""
Power amplifiers testbench for DPD
Just generate, synchronize and demod APKS32 signal
Control a R&S FSW and a R&S SMW200A with pyvisa + NIvisa
Save a *png and *dat (raw-data) files in workdir

@author: Dmitry Stepanov
aug 2018
V1.02

"""

import sys
import time

import visa

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import uic

Ui_MainWindow, QtBaseClass = uic.loadUiType("design.ui") # UI file


class MyApp(QMainWindow):
    """Main class of Apps
    """
    def __init__(self):
        super(MyApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.sA_pushButton.clicked.connect(self.get_spectrum)
        self.ui.genSetUpsA_pushButton.clicked.connect(self.gensetup)
        self.ui.sdat_pushButton.clicked.connect(self.sdat)
        self.ui.spng_pushButton.clicked.connect(self.spng)
        self.ui.ssweep_pushButton.clicked.connect(self.ssweep)
        self.ui.alltest_pushButton.clicked.connect(self.alltest)

    def console_print(self, text):
        """Insert text to consol in UI
        """
        self.ui.plainTextEdit.appendPlainText(text)

    def savedirgen(self):
        """Prepare file's name in the follow format: 
        cf-1e9_srate-10e6_pw10_symLen-32768
        """
        center_frequency = self.ui.cf_lineEdit.text()
        sum_rate = self.ui.sumRate_lineEdit.text()
        reflvl = self.ui.refLevel_lineEdit.text()
        sym_len = self.ui.symLen_lineEdit.text()
        pref = self.ui.saveDir_lineEdit.text()
        time_stamp = time.strftime("%Y/%m/%d-%H:%M:%S", time.localtime())
        save_dir = f"{pref}cf-{(center_frequency)}_srate-{sum_rate}_pwr{reflvl}_symlen-{sym_len}-{time_stamp}"  # Без расширения файла, только имя
        return save_dir

    def sdat(self):
        """Save RAW-file with IQ-data into workdir
        """
        save_dir = "'{}.dat'".format(self.savedirgen())
        fsw_addr = self.ui.ipSA_lineEdit.text()     #Analizer's adress from ui
        rm = visa.ResourceManager()
        try:
            fsw = rm.open_resource(fsw_addr)
            fsw.timeout = 25000
            fsw.encoding = 'latin_1'
            fsw.write_termination = None
            fsw.read_termination = '\n'
            fsw.write("FORMat:DEXPort:DSEParator POINt")
            fsw.write("FORMat:DEXPort:HEADer ON")
            fsw.write("FORMat:DEXPort:MODE RAW")
            fsw.write("MMEMory:STORe1:TRACe 1, {}".format(save_dir))
            self.console_print(f"sdat to {save_dir}")
            fsw.close()
        except visa.VisaIOError as e:
            self.console_print("No fsw connection!")
        except Exception as e:
            print "Error '{0}' occurred. Arguments {1}.".format(e.message, e.args)

    def spng(self):
        """Save screenshot into workdir"""

        print_dir = "'{}.png'".format(self.savedirgen())
        fsw_addr = self.ui.ipSA_lineEdit.text()     #Analizer's adress from ui
        rm = visa.ResourceManager()
        try:
            fsw = rm.open_resource(fsw_addr)
            fsw.timeout = 25000
            fsw.encoding = 'latin_1'
            fsw.write_termination = None
            fsw.read_termination = '\n'
            fsw.write("HCOP:DEST 'MMEM'") #Prints the data to a file.")
            fsw.write("HCOP:DEV:LANG PNG") #Selects bmp as the file format.")
            fsw.write("MMEM:NAME {}".format(print_dir)) #Selects the file name for the printout.
            fsw.write("HCOP:ITEM:ALL") #Prints all screen elements
            fsw.write("HCOP:ITEM:WIND:TEXT '0 dBm power off'") #Adds a comment to the printout.
            fsw.write("HCOP") #//Stores the printout in a file called 'Screenshot.bmp'.
            # FSW.write("HCOP:NEXT") #//Stores the printout in a file called 'Screenshot_001.bmp'.
            self.console_print(f"spng to {print_dir}")
            fsw.close()
        except visa.VisaIOError as e:
            self.console_print("No fsw connection!")
        except Exception as e:
            print "Error '{0}' occurred. Arguments {1}.".format(e.message, e.args)


    def ssweep(self):
        """Make single sweep of analizer, update analizer's data"""

        fsw_addr = self.ui.ipSA_lineEdit.text() #address from ui
        rm = visa.ResourceManager()
        try:
            fsw = rm.open_resource(fsw_addr)
            fsw.timeout = 25000
            fsw.encoding = 'latin_1'
            fsw.write_termination = None
            fsw.read_termination = '\n'
            fsw.write('INIT') #make single sweep
            self.console_print("Done 1-sweep FSW")
            fsw.close()
        except visa.VisaIOError as e:
            self.console_print("No fsw connection!")
        except Exception as e:
            print "Error '{0}' occurred. Arguments {1}.".format(e.message, e.args)

    def gensetup(self):
        """Setup generator with params from UI"""

        smw_addr = self.ui.ipGen_lineEdit.text()
        center_frequency = self.ui.cf_lineEdit.text()
        sum_rate = self.ui.sumRate_lineEdit.text()
        reflvl = self.ui.refLevel_lineEdit.text()
        alpha = self.ui.alpha_lineEdit.text()
        rm = visa.ResourceManager()
        try:
            smw = rm.open_resource(smw_addr)
            smw.timeout = 25000
            smw.encoding = 'latin_1'
            smw.write_termination = None
            smw.read_termination = '\n'
            self.console_print("Connected to " + smw.query('*idn?'))
            smw.write('*cls')
            smw.write('abort')
            smw.write('SOURce1:BB:DM:FORMat APSK32')
            smw.write(':SOURce1:BB:DM:SWITching:STATe 1')
            smw.write(':SOURce1:BB:DM:APSK32:GAMMa G9D10')
            smw.write(':SOURce1:BB:DM:SWITching:STATe 0')
            smw.write(':SOURce1:BB:DM:PRBS:LENGth 20')
            smw.write(':SOURce1:BB:DM:FILTer:TYPE RCOS')
            smw.write(':SOURce1:BB:DM:FILTer:PARameter:RCOSine {}'.format(alpha))
            smw.write(':SOURce1:BB:DM:SRATe {}'.format(sum_rate))
            smw.write(':SOURce1:BB:DM:TRIGger:OUTPut1:ONTime 8')
            smw.write(':SOURce1:BB:DM:TRIGger:OUTPut1:OFFTime 1048567')
            smw.write(':SOURce1:FREQuency:CW {}'.format(center_frequency))
            smw.write(':SOURce1:POWer:POWer {}'.format(reflvl))
            smw.write(':SOURce1:BB:DM:STATe 1')
            smw.write(':OUTPut1:STATe 1')
            smw.write(':SOURce1:INPut:USER3:DIRection OUTP')
            smw.write(':OUTPut1:USER3:SIGNal MARKA1')
            smw.close()
        except visa.VisaIOError as e:
            self.console_print("No fsw connection!")
        except Exception as e:
            print "Error '{0}' occurred. Arguments {1}.".format(e.message, e.args)


    def get_spectrum(self):
        """Setup analizer with params from UI"""

        print("GetSp!")
        fsw_adr = self.ui.ipSA_lineEdit.text()
        center_frequency = self.ui.cf_lineEdit.text()
        sum_rate = self.ui.sumRate_lineEdit.text()
        ref_level = self.ui.refLevel_lineEdit.text()
        alpha = self.ui.alpha_lineEdit.text()
        sym_len = self.ui.symLen_lineEdit.text()
        rm = visa.ResourceManager()
        try:
            fsw = rm.open_resource(fsw_adr)
            fsw.timeout = 10000
            fsw.encoding = 'latin_1'
            fsw.write_termination = None
            fsw.read_termination = '\n'
            self.console_print("Connected to " + fsw.query('*idn?'))
            fsw.write('*rst')
            fsw.write('*cls')
            fsw.write('abort')
            fsw.write('ROSCillator:SOURce E10') #Reference 10 МГц
            #Create new measurement channel for vector signal analysis named "VSA"
            fsw.write("INSTrument:CREate DDEM, 'VSA'")
            fsw.write("INSTrument:SELect 'VSA'") #choose channel VSA
            fsw.write("SYST:PRES:CHAN:EXEC") #preset channel
            fsw.write('FREQ:CENT {}'.format(center_frequency)) #Set the center frequency.
            fsw.write('DISP:TRAC:Y:RLEV {}'.format(ref_level)) #Set the reference level
            #--------- Configuring the expected input signal ---------------
            fsw.write("SENSe:DDEMod:FORMat APSK")  #Set the modulation type
            fsw.write("SENSe:DDEMod:APSK:NSTate 32") #Set the modulation order
            #FSW.write("SENSe:DDEM:MAPP:CAT?") #Query the available symbol mappings for QPSK modulation
            fsw.write("SENSe:DDEM:MAPP 'DVB_S2_910'") #Set the symbol mapping
            fsw.write("SENSe:DDEM:SRAT {}".format(sum_rate))  #Set the symbol rate
            #Select the RRC transmit filter
            fsw.write("SENSe:DDEM:TFIL:NAME 'RRC'")
            fsw.write("SENSe:DDEM:TFIL:ALPH {}".format(alpha))
            fsw.write("TRIGger:SEQuence:SOURce EXTernal") #Choose external trigger EXT1
            fsw.write("INIT:CONT OFF") #switch to single sweep mode
          #//Initiate a basic frequency sweep and wait until the sweep has finished.
            fsw.write("DDEMod:RLENgth:VALue {} SYM".format(sym_len)) #Captured symbols
            fsw.write('DDEMod:TIME {}'.format(sym_len)) # Viewed symbols
            fsw.close()
        except visa.VisaIOError as e:
            self.console_print("No fsw connection!")
        except Exception as e:
            print ("Error '{0}' occurred. Arguments {1}.".format(e.message, e.args))


    def alltest(self):
        """Start all testing procedure one by one"""

        try:
            self.gensetup()
            self.get_spectrum()
            self.ssweep()
            self.spng()
            self.sdat()
        except visa.VisaIOError as e:
            self.console_print("Something wrong!")
        except Exception as e:
            print "Error '{0}' occurred. Arguments {1}.".format(e.message, e.args)



if __name__ == "__main__":
    APP = QApplication(sys.argv)
    WINDOW = MyApp()
    WINDOW.show()
#    sys.exit(app.exec_()) #does't work in spyder
    exit(APP.exec_())

