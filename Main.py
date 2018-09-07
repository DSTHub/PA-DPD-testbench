"""
Power amplifiers testbench for DPD
Just generate, synchronize and demod APKS32 signal 
Control a FSW16 and a SMW200A by pyvisa + NIvisa
Save a *png and *dat (raw-data) files

@author: Dmitry Stepanov
aug 2018
V1.01

"""

import sys, time
import os

import visa

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import uic

Ui_MainWindow, QtBaseClass = uic.loadUiType("design.ui") # UI file


class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.sA_pushButton.clicked.connect(self.GetSp)
        self.ui.genSetUpsA_pushButton.clicked.connect(self.gensetup)
        self.ui.sdat_pushButton.clicked.connect(self.sdat)
        self.ui.spng_pushButton.clicked.connect(self.spng)
        self.ui.ssweep_pushButton.clicked.connect(self.ssweep)
        self.ui.alltest_pushButton.clicked.connect(self.alltest)
        
    def console_print(self, text):
        self.ui.plainTextEdit.appendPlainText(text)
    
    def savedirgen(self): # Формат файлов и пути для сохранения cf-1e9_srate-10e6_pw10_symLen-32768
        cf = self.ui.cf_lineEdit.text()
        sumRate = self.ui.sumRate_lineEdit.text()
        reflvl = self.ui.refLevel_lineEdit.text()
        symLen = self.ui.symLen_lineEdit.text()
        pref = self.ui.saveDir_lineEdit.text()
        time_stamp = time.strftime("%Y/%m/%d-%H:%M:%S", time.localtime())
        save_dir = f"{pref}cf-{(cf)}_srate-{sumRate}_pwr{reflvl}_symlen-{symLen}-{time_stamp}"  # Без расширения файла, только имя
        return (save_dir)
        
    
    def sdat(self): # Сохранить WAR файл IQ в рабочую папку 
        save_dir = "'{}.dat'".format(self.savedirgen())
        FSW_addr = self.ui.ipSA_lineEdit.text()     #Адрес анализатора в окне ui 
        rm = visa.ResourceManager()
        try:
            FSW = rm.open_resource(FSW_addr)
            FSW.timeout = 25000
            FSW.encoding = 'latin_1'
            FSW.write_termination = None
            FSW.read_termination = '\n'
            FSW.write("FORMat:DEXPort:DSEParator POINt")
            FSW.write("FORMat:DEXPort:HEADer ON")
            FSW.write("FORMat:DEXPort:MODE RAW")
            FSW.write("MMEMory:STORe1:TRACe 1, {}".format(save_dir))
            self.console_print(f"sdat to {save_dir}")
            FSW.close()
        except:
            self.console_print("No fsw connection!")
        
    def spng(self): # Сохранить скриншот в рабочую папку 
        
        print_dir = "'{}.png'".format(self.savedirgen())
        FSW_addr = self.ui.ipSA_lineEdit.text()     #Адрес анализатора в окне ui 
        rm = visa.ResourceManager()
        try:
            FSW = rm.open_resource(FSW_addr)
            FSW.timeout = 25000
            FSW.encoding = 'latin_1'
            FSW.write_termination = None
            FSW.read_termination = '\n'
            FSW.write("HCOP:DEST 'MMEM'") #Prints the data to a file.")
            FSW.write("HCOP:DEV:LANG PNG") #Selects bmp as the file format.")
            FSW.write("MMEM:NAME {}".format(print_dir)) #Selects the file name for the printout.
            FSW.write("HCOP:ITEM:ALL") #Prints all screen elements
            FSW.write("HCOP:ITEM:WIND:TEXT '0 dBm power off'") #Adds a comment to the printout.
            FSW.write("HCOP") #//Stores the printout in a file called 'Screenshot.bmp'.
            # FSW.write("HCOP:NEXT") #//Stores the printout in a file called 'Screenshot_001.bmp'.
            self.console_print(f"spng to {print_dir}")
            FSW.close()
        except:
            self.console_print("No fsw connection!")        
              
    def ssweep(self):
        FSW_addr = self.ui.ipSA_lineEdit.text()     #Адрес анализатора в окне ui 
        rm = visa.ResourceManager()
        try:
            FSW = rm.open_resource(FSW_addr)
            FSW.timeout = 25000
            FSW.encoding = 'latin_1'
            FSW.write_termination = None
            FSW.read_termination = '\n'
            FSW.write('INIT')                       #сделать однократный запуск
            self.console_print("Done 1-sweep FSW")
            FSW.close()
        except:
            self.console_print("No fsw connection!")    

    def gensetup(self):
        SMW_addr = self.ui.ipGen_lineEdit.text()
        cf = self.ui.cf_lineEdit.text()
        sumRate = self.ui.sumRate_lineEdit.text()
        reflvl = self.ui.refLevel_lineEdit.text()
        alpha = self.ui.alpha_lineEdit.text()
        
        rm = visa.ResourceManager()
        try:
            SMW = rm.open_resource(SMW_addr)
            SMW.timeout = 25000
            SMW.encoding = 'latin_1'
            SMW.write_termination = None
            SMW.read_termination = '\n'
            self.console_print("Connected to " + SMW.query('*idn?'))

            SMW.write('*cls')
            SMW.write('abort')
            
            """#################CONFIGURE INSTRUMENT#################"""
                    
            SMW.write('SOURce1:BB:DM:FORMat APSK32')
            SMW.write(':SOURce1:BB:DM:SWITching:STATe 1')
            SMW.write(':SOURce1:BB:DM:APSK32:GAMMa G9D10')
            SMW.write(':SOURce1:BB:DM:SWITching:STATe 0')
            SMW.write(':SOURce1:BB:DM:PRBS:LENGth 20')
            SMW.write(':SOURce1:BB:DM:FILTer:TYPE RCOS')
            
            SMW.write(':SOURce1:BB:DM:FILTer:PARameter:RCOSine {}'.format(alpha))
            
            SMW.write(':SOURce1:BB:DM:SRATe {}'.format(sumRate))
            
            SMW.write(':SOURce1:BB:DM:TRIGger:OUTPut1:ONTime 8')
            
            SMW.write(':SOURce1:BB:DM:TRIGger:OUTPut1:OFFTime 1048567')
            
            SMW.write(':SOURce1:FREQuency:CW {}'.format(cf))
            
            SMW.write(':SOURce1:POWer:POWer {}'.format(reflvl))
            
            SMW.write(':SOURce1:BB:DM:STATe 1')
            
            SMW.write(':OUTPut1:STATe 1')
            SMW.write(':SOURce1:INPut:USER3:DIRection OUTP')
            SMW.write(':OUTPut1:USER3:SIGNal MARKA1')
            SMW.close()
        except:
            self.console_print("No SMW connection!") 

    def GetSp(self):
        print("GetSp!")
        # Создаем объект и настраиваеи его
        FSW_adr = self.ui.ipSA_lineEdit.text()
        cf = self.ui.cf_lineEdit.text()
        sumRate = self.ui.sumRate_lineEdit.text()
        refLevel = self.ui.refLevel_lineEdit.text()
        alpha = self.ui.alpha_lineEdit.text()
        symLen = self.ui.symLen_lineEdit.text()
        
        rm = visa.ResourceManager()
        try:
            FSW = rm.open_resource(FSW_adr)
            FSW.timeout = 10000
            FSW.encoding = 'latin_1'
            FSW.write_termination = None
            FSW.read_termination = '\n'
            self.console_print("Connected to " + FSW.query('*idn?'))
            
            FSW.write('*rst')
            FSW.write('*cls')
            FSW.write('abort')
            FSW.write('ROSCillator:SOURce E10') #Внешний опорный сигнал 10 МГц 
            #Create new measurement channel for vector signal analysis named "VSA"
            FSW.write("INSTrument:CREate DDEM, 'VSA'")
            FSW.write("INSTrument:SELect 'VSA'") #выбираем канал VSA
            FSW.write("SYST:PRES:CHAN:EXEC") #Делаем пресет канала VSA
            FSW.write('FREQ:CENT {}'.format(cf)) #Set the center frequency.
            FSW.write('DISP:TRAC:Y:RLEV {}'.format(refLevel)) #Set the reference level
            #--------- Configuring the expected input signal ---------------
            FSW.write("SENSe:DDEMod:FORMat APSK")  #Set the modulation type
            FSW.write("SENSe:DDEMod:APSK:NSTate 32") #Set the modulation order
            #FSW.write("SENSe:DDEM:MAPP:CAT?") #Query the available symbol mappings for QPSK modulation
            FSW.write("SENSe:DDEM:MAPP 'DVB_S2_910'") #Set the symbol mapping
            FSW.write("SENSe:DDEM:SRAT {}".format(sumRate))  #Set the symbol rate
            #Select the RRC transmit filter
            FSW.write("SENSe:DDEM:TFIL:NAME 'RRC'")
            FSW.write("SENSe:DDEM:TFIL:ALPH {}".format(alpha))
        
        
            FSW.write("TRIGger:SEQuence:SOURce EXTernal") #Переключаем тригер на EXT1
        
            FSW.write("INIT:CONT OFF") #switch to single sweep mode
          #//Initiate a basic frequency sweep and wait until the sweep has finished.
            FSW.write("DDEMod:RLENgth:VALue {} SYM".format(symLen)) #захватываемое колличество символов
            FSW.write('DDEMod:TIME {}'.format(symLen)) # колличество символов, отобр на экране
            FSW.close()
        except:
            self.console_print("No fsw connection!") 
        
    def alltest(self):
        try:
            self.gensetup()
            self.GetSp()
            self.ssweep()
            self.spng()
            self.sdat()
        except:
            print("not works")
        
       
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
#    sys.exit(app.exec_()) #does't work in spyder
    exit(app.exec_())
