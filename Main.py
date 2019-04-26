"""
Power amplifiers testbench for DPD
Just generate, synchronize and demod APKS32 signal
Control a FSW16 and a SMW200A by pyvisa + NIvisa
Save a *png and *dat (raw-data) files

@author: Dmitry Stepanov
sep 2018
V2.02

"""

import sys
import time
import fsw
import smw
import comsender
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import uic

Ui_MainWindow, QtBaseClass = uic.loadUiType("design.ui")  # UI file

visatimeout = 250  # Timeout in msec for each opened resource


class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.fsw = fsw.Fsw(
            addr=self.ui.ipSA_lineEdit.text(),
            backend=self.ui.backendComboBox.currentText())
        self.fsw.preconfig()

        self.smw = smw.Smw(
            addr=self.ui.ipGen_lineEdit.text(),
            backend=self.ui.backendComboBox.currentText())
        self.smw.preconfig()

        self.comsender = comsender.Comsender()
        self.comsender.preconfig()

        self.ui_fsw_addr = self.ui.ipSA_lineEdit.text()  # FSW's address from ui

        self.ui.initSa_pushButton.clicked.connect(self.aninit)
        self.ui.initGen_pushButton.clicked.connect(self.geninit)
        self.ui.sdat_pushButton.clicked.connect(self.sdat)
        self.ui.spng_pushButton.clicked.connect(self.spng)
        self.ui.ssweep_pushButton.clicked.connect(self.ssweep)
        self.ui.alltest_pushButton.clicked.connect(self.alltest)
        self.ui.wrParAn_pushButton.clicked.connect(self.wrParAn)
        self.ui.wrParGen_pushButton.clicked.connect(self.wrParGen)

        self.ui.initInst_pushButton.clicked.connect(self.comsenderInit)
        self.ui.comWr_pushButton.clicked.connect(self.comsenderWr)
        self.ui.comRead_pushButton.clicked.connect(self.comsenderRead)
        self.ui.ComQ_pushButton.clicked.connect(self.comsenderQ)

#        self.ui.alpha_lineEdit.editingFinished.connect(self.ssweep)
#        self.ui.modType_comboBox.activated.connect(self.spng)

    def console_print(self, text):   
        """
        Apend 'text' into ui.plainTextEdit (ui console)
        
        :param text:    text to apend into ui.plainTextEdit (ui console), str
        :return:        None
        """
        self.ui.plainTextEdit.appendPlainText(text)

    # File's name format cf-1e9_srate-10e6_pw10_symLen-32768 + PATH workdir
    # from ui
    def __savedirgen(self):
        cf = self.ui.cf_lineEdit.text()
        sumRate = self.ui.sumRate_lineEdit.text()
        powerLevel = self.ui.powerLevel_lineEdit.text()
        symLen = self.ui.symLen_lineEdit.text()
        pref = self.ui.saveDir_lineEdit.text()
        time_stamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        # Без расширения файла, только имя
        save_dir = f"{pref}cf-{(cf)}_srate-{sumRate}_pwr-{powerLevel}_len-{symLen}-{time_stamp}"
        return (save_dir)

    def sdat(self):  
        """
        Save RAW-file IQ into work dir
        """
        save_dir = self.__savedirgen()
        # call Fsw.saveData(), return resp into ui.plainTextEdit
        self.console_print(self.fsw.saveData(save_dir))

    def spng(self):  # Save a screenshot into workdir
        print_dir = self.__savedirgen()
        # call Fsw.savePng(), return resp into ui.plainTextEdit
        self.console_print(self.fsw.savePng(print_dir))

    def ssweep(self):
        # call Fsw.sweep(), return resp into ui.plainTextEdit
        self.console_print(self.fsw.ssweep())

    def geninit(self):
        """
        Initialize R&S SMW200A attributes, try connect via visa

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
            self.console_print(
                self.smw.initDPDtestBench(
                    alpha, sumRate, cf, power))
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
        fsw_addr = self.ui.ipSA_lineEdit.text()  # FSW addr from UI
        self.fsw.addr = fsw_addr
        self.fsw.backend = self.ui.backendComboBox.currentText()
        self.console_print(self.fsw.connect())
        self.fsw.preconfig()

        if self.fsw.check_connection:
            self.console_print(
                self.fsw.initDPDtestBench(
                    cf, reflvl, sumRate, alpha, symLen))
        else:
            self.console_print('Check FSW settings!')

    def wrParAn(self):
        """
        Write parameters from UI to analyzer  
        """
        cf = self.ui.cf_lineEdit.text()
        reflvl = self.ui.refLevel_lineEdit.text()
        sumRate = self.ui.sumRate_lineEdit.text()
        alpha = self.ui.alpha_lineEdit.text()
        symLen = self.ui.symLen_lineEdit.text()
        self.console_print(
            self.fsw.initDPDtestBench(
                cf, reflvl, sumRate, alpha, symLen))

    def wrParGen(self):
        """
        Write parameters from UI to signal generator  
        """
        cf = self.ui.cf_lineEdit.text()
        sumRate = self.ui.sumRate_lineEdit.text()
        power = self.ui.powerLevel_lineEdit.text()
        alpha = self.ui.alpha_lineEdit.text()
        self.console_print(
            self.smw.initDPDtestBench(
                alpha, sumRate, cf, power))

    def alltest(self):
        #        try:
        self.wrParGen()
        self.wrParAn()
        self.fsw.ssweep()
        self.fsw.saveData(self.__savedirgen())
        self.fsw.savePng(self.__savedirgen())
#        except:
#            print("not works")

    def comsenderInit(self):
        """
        Init comsender
        """
        self.console_print("Comsender's Instrument init...")
        self.comsender.addr = self.ui.ipInst_lineEdit.text()
        self.comsender.backend = "@ni"
        self.console_print(self.comsender.connect())
        self.fsw.preconfig()

    def comsenderWr(self):
        """
        Write command from UI to visa instrument  
        """
        self.console_print(
            self.comsender.write(
                self.ui.command_lineEdit.text()))

    def comsenderRead(self):
        """
        Read data from visa instrument  
        """
        self.console_print(self.comsender.read())

    def comsenderQ(self):
        """
        Write command from UI to visa instrument then 
        Read data from visa instrument
        """
        self.console_print(
            self.comsender.query(
                self.ui.command_lineEdit.text()))


if __name__ == "__main__":
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance() 
    window = MyApp()
    window.show()
    app.exec_()

