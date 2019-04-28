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

VISATIMEOUT = 250  # Timeout in msec for each opened resource


class MyApp(QMainWindow):
    """Main class of Apps"""

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

        self.ui.initSa_pushButton.clicked.connect(self.an_init)
        self.ui.initGen_pushButton.clicked.connect(self.gen_init)
        self.ui.sdat_pushButton.clicked.connect(self.save_data)
        self.ui.spng_pushButton.clicked.connect(self.save_png)
        self.ui.ssweep_pushButton.clicked.connect(self.single_sweep)
        self.ui.alltest_pushButton.clicked.connect(self.all_test)
        self.ui.wrParAn_pushButton.clicked.connect(self.wr_par_an)
        self.ui.wrParGen_pushButton.clicked.connect(self.wr_par_gen)

        self.ui.initInst_pushButton.clicked.connect(self.comsender_init)
        self.ui.comWr_pushButton.clicked.connect(self.comsender_write)
        self.ui.comRead_pushButton.clicked.connect(self.comsender_read)
        self.ui.ComQ_pushButton.clicked.connect(self.comsender_query)

#        self.ui.alpha_lineEdit.editingFinished.connect(self.ssweep)
#        self.ui.modType_comboBox.activated.connect(self.spng)

    def console_print(self, text):
        """
        Apend 'text' into ui.plainTextEdit (ui console)

        :param text:    text to apend into ui.plainTextEdit (ui console), str
        :return:        None
        """
        self.ui.plainTextEdit.appendPlainText(text)

    def __savedirgen(self):
        """Prepare file's name in format:
            cf-1e9_srate-10e6_pw10_symLen-32768 + PATH workdir"""

        center_frequency = self.ui.cf_lineEdit.text()
        sum_rate = self.ui.sumRate_lineEdit.text()
        power_level = self.ui.powerLevel_lineEdit.text()
        sym_len = self.ui.symLen_lineEdit.text()
        pref = self.ui.saveDir_lineEdit.text()
        time_stamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        # Без расширения файла, только имя
        save_dir = f"{pref}cf-{(center_frequency)}_srate-{sum_rate}_pwr-{power_level}_len-{sym_len}-{time_stamp}"
        return save_dir

    def save_data(self):
        """
        Save RAW-file IQ into workdir
        """
        save_dir = self.__savedirgen()
        # call Fsw.saveData(), return resp into ui.plainTextEdit
        self.console_print(self.fsw.saveData(save_dir))

    def save_png(self):
        """Save a screenshot into workdir"""

        print_dir = self.__savedirgen()
        # call Fsw.savePng(), return resp into ui.plainTextEdit
        self.console_print(self.fsw.savePng(print_dir))

    def single_sweep(self):
        """call Fsw.sweep(), return resp into ui.plainTextEdit"""

        self.console_print(self.fsw.ssweep())

    def gen_init(self):
        """
        Initialize R&S SMW200A attributes, try connect via visa

        """
        center_frequency = self.ui.cf_lineEdit.text()
        sum_rate = self.ui.sumRate_lineEdit.text()
        power = self.ui.powerLevel_lineEdit.text()
        alpha = self.ui.alpha_lineEdit.text()
        smw_addr = self.ui.ipGen_lineEdit.text()
        self.smw.addr = smw_addr
        self.smw.backend = self.ui.backendComboBox.currentText()
        self.console_print(self.smw.connect())
        self.smw.preconfig()
        if self.smw.check_connection:
            self.console_print(
                self.smw.initDPDtestBench(
                    alpha, sum_rate, center_frequency, power))
        else:
            self.console_print('Check SMW200A settings!')

    def an_init(self):
        """Initialize R&S FSW attributes, try connect via visa
                self.console_print("Connected to " + FSW.query('*idn?'))
        """
        center_frequency = self.ui.cf_lineEdit.text()
        ref_lvl = self.ui.refLevel_lineEdit.text()
        sum_rate = self.ui.sumRate_lineEdit.text()
        alpha = self.ui.alpha_lineEdit.text()
        sym_len = self.ui.symLen_lineEdit.text()
        fsw_addr = self.ui.ipSA_lineEdit.text()  # FSW addr from UI
        self.fsw.addr = fsw_addr
        self.fsw.backend = self.ui.backendComboBox.currentText()
        self.console_print(self.fsw.connect())
        self.fsw.preconfig()

        if self.fsw.check_connection:
            self.console_print(
                self.fsw.initDPDtestBench(
                    center_frequency, ref_lvl, sum_rate, alpha, sym_len))
        else:
            self.console_print('Check FSW settings!')

    def wr_par_an(self):
        """
        Write parameters from UI to analyzer
        """
        center_frequency = self.ui.cf_lineEdit.text()
        ref_lvl = self.ui.refLevel_lineEdit.text()
        sum_rate = self.ui.sumRate_lineEdit.text()
        alpha = self.ui.alpha_lineEdit.text()
        sym_len = self.ui.symLen_lineEdit.text()
        self.console_print(
            self.fsw.initDPDtestBench(
                center_frequency, ref_lvl, sum_rate, alpha, sym_len))

    def wr_par_gen(self):
        """
        Write parameters from UI to signal generator
        """
        center_frequency = self.ui.cf_lineEdit.text()
        sum_rate = self.ui.sumRate_lineEdit.text()
        power = self.ui.powerLevel_lineEdit.text()
        alpha = self.ui.alpha_lineEdit.text()
        self.console_print(
            self.smw.initDPDtestBench(
                alpha, sum_rate, center_frequency, power))

    def all_test(self):
        """Start all testing procedure one by one"""

        #        try:
        self.wrParGen()
        self.wrParAn()
        self.fsw.ssweep()
        self.fsw.saveData(self.__savedirgen())
        self.fsw.savePng(self.__savedirgen())
#        except:
#            print("not works")

    def comsender_init(self):
        """
        Init comsender
        """
        self.console_print("Comsender's Instrument init...")
        self.comsender.addr = self.ui.ipInst_lineEdit.text()
        self.comsender.backend = "@ni"
        self.console_print(self.comsender.connect())
        self.fsw.preconfig()

    def comsender_write(self):
        """Write command from UI to visa instrument"""

        self.console_print(
            self.comsender.write(
                self.ui.command_lineEdit.text()))

    def comsender_read(self):
        """Read data from visa instrument"""

        self.console_print(self.comsender.read())

    def comsender_query(self):
        """
        Write command from UI to visa instrument then
        Read data from visa instrument
        """
        self.console_print(
            self.comsender.query(
                self.ui.command_lineEdit.text()))


if __name__ == "__main__":
    if not QApplication.instance():
        APP = QApplication(sys.argv)
    else:
        APP = QApplication.instance()
    WINDOW = MyApp()
    WINDOW.show()
    APP.exec_()

