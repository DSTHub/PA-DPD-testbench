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
import fsw
import smw

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import uic

Ui_MainWindow, QtBaseClass = uic.loadUiType("design.ui") # UI file

visatimeout = 250   #Timeout in msec for each opened resource
        
class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.fsw = fsw.Fsw(addr	= self.ui.ipSA_lineEdit.text(), backend = self.ui.backendComboBox.currentText())
        self.fsw.preconfig()
        
        self.smw = smw.Smw(addr	= self.ui.ipGen_lineEdit.text(), backend = self.ui.backendComboBox.currentText())
        self.smw.preconfig()

        self.ui_fsw_addr = self.ui.ipSA_lineEdit.text()     #FSW's address from ui

        self.ui.initSa_pushButton.clicked.connect(self.aninit)
        self.ui.initGen_pushButton.clicked.connect(self.geninit)
        self.ui.sdat_pushButton.clicked.connect(self.sdat)
        self.ui.spng_pushButton.clicked.connect(self.spng)
        self.ui.ssweep_pushButton.clicked.connect(self.ssweep)
        self.ui.alltest_pushButton.clicked.connect(self.alltest)
        self.ui.wrParAn_pushButton.clicked.connect(self.wrParAn)
        self.ui.wrParGen_pushButton.clicked.connect(self.wrParGen)
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
        
    def sdat(self): # Сохранить RAW файл IQ в рабочую папку 
        save_dir = self.savedirgen()
        self.console_print(self.fsw.saveData(save_dir)) #call Fsw.saveData(), return resp into ui.plainTextEdit
        
    def spng(self): # Save a screenshot into workdir
        print_dir = self.savedirgen()
        self.console_print(self.fsw.savePng(print_dir)) #call Fsw.savePng(), return resp into ui.plainTextEdit
                      
    def ssweep(self):
        self.console_print(self.fsw.ssweep()) #call Fsw.sweep(), return resp into ui.plainTextEdit
   

    def geninit(self):
        """Initialize R&S SMW200A attributes, try connect via visa

        """
        cf = self.ui.cf_lineEdit.text()
        sumRate = self.ui.sumRate_lineEdit.text()
        power = self.ui.powerLevel_lineEdit.text()
        alpha = self.ui.alpha_lineEdit.text()
        SMW_addr = self.ui.ipGen_lineEdit.text()
        self.smw.addr = SMW_addr
        self.smw.backend = self.ui.backendComboBox.currentText()
        self.console_print(self.smw.connect())
        self.smw.preconfig()
        if self.smw.check_connection:
            self.console_print(self.smw.initDPDtestBench(alpha, sumRate, cf, power))
        else:
            self.console_print('Check SMW200A settings!')


    def aninit(self):
        """Initialize R&S FSW attributes, try connect via visa
        
        
		self.console_print("Connected to " + FSW.query('*idn?'))
        """

        cf = self.ui.cf_lineEdit.text()
        reflvl = self.ui.refLevel_lineEdit.text()
        sumRate = self.ui.sumRate_lineEdit.text()
        alpha = self.ui.alpha_lineEdit.text()
        symLen = self.ui.symLen_lineEdit.text()
        fsw_addr = self.ui.ipSA_lineEdit.text()     #FSW addr from UI 
        self.fsw.addr = fsw_addr
        self.fsw.backend = self.ui.backendComboBox.currentText()
        self.console_print(self.fsw.connect())
        self.fsw.preconfig()

        if self.fsw.check_connection:
            self.console_print(self.fsw.initDPDtestBench(cf, reflvl, sumRate, alpha, symLen))
        else:
            self.console_print('Check FSW settings!')
    
    def wrParAn(self):
        cf = self.ui.cf_lineEdit.text()
        reflvl = self.ui.refLevel_lineEdit.text()
        sumRate = self.ui.sumRate_lineEdit.text()
        alpha = self.ui.alpha_lineEdit.text()
        symLen = self.ui.symLen_lineEdit.text()        
        self.console_print(self.fsw.initDPDtestBench(cf, reflvl, sumRate, alpha, symLen))
    
    def wrParGen(self):
        cf = self.ui.cf_lineEdit.text()
        sumRate = self.ui.sumRate_lineEdit.text()
        power = self.ui.powerLevel_lineEdit.text()
        alpha = self.ui.alpha_lineEdit.text()
        self.console_print(self.smw.initDPDtestBench(alpha, sumRate, cf, power))


    def alltest(self):
#        try:
        self.geninit()
        self.aninit()
        self.fsw.ssweep()
        self.fsw.saveData(self.savedirgen())
        self.fsw.savePng(self.savedirgen())
#        except:
#            print("not works")
            

       
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    exit(app.exec_())
#    sys.exit(app.exec_()) #does't work in spyder
    
