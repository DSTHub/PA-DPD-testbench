"""
Power amplifiers testbench for DPD
Just generate, synchronize and demod APKS32 signal 
Control a FSW16 and a SMW200A by pyvisa + NIvisa
Save a *png and *dat (raw-data) files

@author: Dmitry Stepanov
sep 2018
V2.01  

"""

import sys
import time
import os

import visa
import fsw

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import uic

Ui_MainWindow, QtBaseClass = uic.loadUiType("design.ui") # UI file

visatimeout = 250   #Timeout in msec for each opened resource
        
class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.fsw = fsw.Fsw()
        self.fsw.preconfig()
        
        self.ui_fsw_addr = self.ui.ipSA_lineEdit.text()     #FSW's address from ui

        self.ui.sA_pushButton.clicked.connect(self.GetSp)
        self.ui.genSetUpsA_pushButton.clicked.connect(self.gensetup)
        self.ui.sdat_pushButton.clicked.connect(self.sdat)
        self.ui.spng_pushButton.clicked.connect(self.spng)
        self.ui.ssweep_pushButton.clicked.connect(self.ssweep)
        self.ui.alltest_pushButton.clicked.connect(self.alltest)
#        self.ui.alpha_lineEdit.editingFinished.connect(self.ssweep)
#        self.ui.modType_comboBox.activated.connect(self.spng)
        
        
        
    def console_print(self, text):  #Apend 'text' into ui.plainTextEdit (ui console)
        self.ui.plainTextEdit.appendPlainText(text)
    
    def savedirgen(self): # File's name format cf-1e9_srate-10e6_pw10_symLen-32768 + PATH workdir from ui
        cf = self.ui.cf_lineEdit.text()
        sumRate = self.ui.sumRate_lineEdit.text()
        reflvl = self.ui.refLevel_lineEdit.text()
        symLen = self.ui.symLen_lineEdit.text()
        pref = self.ui.saveDir_lineEdit.text()
        time_stamp = time.strftime("%Y/%m/%d-%H:%M:%S", time.localtime())
        save_dir = f"{pref}cf-{(cf)}_srate-{sumRate}_pwr{reflvl}_symlen-{symLen}-{time_stamp}"  # Без расширения файла, только имя
        return (save_dir)
        
    def sdat(self): # Сохранить WAR файл IQ в рабочую папку 
        save_dir = self.savedirgen()
        self.console_print(self.fsw.save_dat(save_dir)) #call Fsw.save_dat(), return resp into ui.plainTextEdit
        
    def spng(self): # Save a screenshot into workdir
        print_dir = self.savedirgen()
        self.console_print(self.fsw.save_png(print_dir)) #call Fsw.save_png(), return resp into ui.plainTextEdit
                      
    def ssweep(self):
        self.console_print(self.fsw.ssweep()) #call Fsw.sweep(), return resp into ui.plainTextEdit
   

    def gensetup(self):
        SMW_addr = self.ui.ipGen_lineEdit.text()
        cf = self.ui.cf_lineEdit.text()
        sumRate = self.ui.sumRate_lineEdit.text()
        reflvl = self.ui.refLevel_lineEdit.text()
        alpha = self.ui.alpha_lineEdit.text()
        
        rm = visa.ResourceManager()
        
        
        try:
            SMW = rm.open_resource(SMW_addr)
            SMW.timeout = visatimeout
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
        """Initialize R&S FSW attributes, try connect via visa
        
        
self.console_print("Connected to " + FSW.query('*idn?'))
        """

        if  self.fsw.check_connection:
            cf = self.ui.cf_lineEdit.text()
            sumRate = self.ui.sumRate_lineEdit.text()
            refLevel = self.ui.refLevel_lineEdit.text()
            alpha = self.ui.alpha_lineEdit.text()
            symLen = self.ui.symLen_lineEdit.text()
            self.fsw.write('*rst')
            self.fsw.write('*cls')
            self.fsw.write('abort')
            self.fsw.write('ROSCillator:SOURce E10') #Внешний опорный сигнал 10 МГц 
            #Create new measurement channel for vector signal analysis named "VSA"
            self.fsw.write("INSTrument:CREate DDEM, 'VSA'")
            self.fsw.write("INSTrument:SELect 'VSA'") #выбираем канал VSA
            self.fsw.write("SYST:PRES:CHAN:EXEC") #Делаем пресет канала VSA
            self.fsw.write('FREQ:CENT {}'.format(cf)) #Set the center frequency.
            self.fsw.write('DISP:TRAC:Y:RLEV {}'.format(refLevel)) #Set the reference level
            #--------- Configuring the expected input signal ---------------
            self.fsw.write("SENSe:DDEMod:FORMat APSK")  #Set the modulation type
            self.fsw.write("SENSe:DDEMod:APSK:NSTate 32") #Set the modulation order
            #FSW.write("SENSe:DDEM:MAPP:CAT?") #Query the available symbol mappings for QPSK modulation
            self.fsw.write("SENSe:DDEM:MAPP 'DVB_S2_910'") #Set the symbol mapping
            self.fsw.write("SENSe:DDEM:SRAT {}".format(sumRate))  #Set the symbol rate
            #Select the RRC transmit filter
            self.fsw.write("SENSe:DDEM:TFIL:NAME 'RRC'")
            self.fsw.write("SENSe:DDEM:TFIL:ALPH {}".format(alpha))
            self.fsw.write("TRIGger:SEQuence:SOURce EXTernal") #Переключаем тригер на EXT1
            self.fsw.write("INIT:CONT OFF") #switch to single sweep mode
          #//Initiate a basic frequency sweep and wait until the sweep has finished.
            self.fsw.write("DDEMod:RLENgth:VALue {} SYM".format(symLen)) #захватываемое колличество символов
            self.fsw.write('DDEMod:TIME {}'.format(symLen)) # колличество символов, отобр на экране
            self.console_print("FSW configured") 
        except:
            self.console_print("No fsw connection!") 
            
            if not self.fsw.check_connection:
                FSW_adr = self.ui.ipSA_lineEdit.text()
                self.fsw.addr = FSW_adr
                self.console_print(self.fsw.connect())
                self.fsw.preconfig()
        
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
