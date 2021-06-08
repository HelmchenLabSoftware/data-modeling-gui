'''
TODO:
    * Data Summary:
        - Number of points
        - Automatically identify categorical variables
        - For categorical variables plot all values
        - For continuous variables plot mean and std
    * Plot Types
        * 1D
        * Scatter
        * BoxPlot / Violin
            - Allow multiselect categoric columns
        * PairPlot
        * Signal Processing: ACF/PACF/PSD
    * Data Augmentation
        - Parse as datetime
        - Right click delete column
        - Add enum column
        - Add function of column
    * Model Fitting
        * OLS - Select vars, use autodetected categorical, report F-Statistic
        * OLS CrossValidate
            - Select vars, CV method, accuracy metric
            - Regularization sweep plot,
            - Train/test accuracy
            - Plot train/test examples
        * Bayesian ??
'''


###############################
# Import system libraries
###############################
import os, sys, locale
from functools import partial
import json
import numpy as np
import pandas as pd
from PyQt5 import QtGui, QtCore, QtWidgets

#######################################
# Import local libraries
#######################################

import src.lib.qt_gui_helper as qt_helper
from src.lib.mpl_qt import MplPlotLayout
import src.lib.plots as plot_helper
# from mesostat.utils.system import getfiles, getfiles_walk
# from mesostat.utils.strings import path_extract_data

#######################################
# Compile QT File
#######################################
thisdir = os.path.dirname(os.path.abspath(__file__))
qt_helper.compile_form(os.path.join(thisdir, 'DataModeling', 'datamodelinggui.ui'))

#######################################
# Load compiled forms
#######################################
from src.DataModeling.datamodelinggui import Ui_DataModelingGUI


#######################################################
# Main Window
#######################################################
class DataModelingGUI():
    def __init__(self, dialog):
        # Init
        self.dialog = dialog
        self.gui = Ui_DataModelingGUI()
        self.gui.setupUi(dialog)

        # GUI-Constants
        self.pathSettings = os.path.join(thisdir, 'settings.json')
        if not os.path.isfile(self.pathSettings):
            print('No settings file found, creating new')
            self.settings = {'fontsize' : 15, 'pathdata' : './'}
        else:
            self.load_settings()

        # Variables
        self.data = {}
        self.plotFunctions = {
            '1D Plot':                  plot_helper.plot1D,
            'Autocorrelation':          plot_helper.plotACF,
            'Partial Autocorrelation':  plot_helper.plotPACF,
            'BoxPlot':                  plot_helper.plotBox,
            'ViolinPlot':               plot_helper.plotViolin
        }
        self.timeFunctionDict = {
            'second':   lambda t: t.second,
            'minute':   lambda t: t.minute,
            'hour':     lambda t: t.hour,
            'day':      lambda t: t.day,
            'month':    lambda t: t.month,
            'year':     lambda t: t.year
        }
        # self.timeMenuResponseDict = {timeType : lambda: self.data_parse_col_datetime(timeType) for timeType in self.timeFunctionDict.keys()}


        # Update font size
        self.update_system_font_size()

        # Objects and initialization
        self._init_plot_layout()

        # Reacts
        self.dialog.key_press_event = self.key_press_event
        self.gui.dataTableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.gui.dataTableWidget.customContextMenuRequested.connect(self._react_datatable_dropdown_menu)
        self.gui.plotButton.clicked.connect(self.plot_data)

        # File menu actions
        self.gui.actionLoad_CSV.triggered.connect(self.load_data_csv)

        self.gui.actionLoad_CSV.setShortcut('Ctrl+o')

    def _warning(self, *args):
        message = ' '.join([str(s) for s in args])
        msgBox = QtWidgets.QMessageBox(self.gui.centralWidget)
        msgBox.setText(message)
        msgBox.exec()

    def load_settings(self):
        with open(self.pathSettings, 'r') as f:
            self.settings = json.load(f)

    def save_settings(self):
        with open(self.pathSettings, 'w') as f:
            json.dump(self.settings, f)
        print('saved settings', self.settings)

    def _init_plot_layout(self):
        self.plotlayout = MplPlotLayout(self.dialog, width=5, height=4, dpi=100)
        layout = self.gui.plotTab.layout()

        layout.addWidget(self.plotlayout.widget)
        self.plotlayout.canvas.axes.plot([0,1,2,3,4], [10,1,20,3,40])

    def load_data_csv(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self.gui.centralWidget, "Get data directory",
                                                      self.settings['pathdata'], 'CSV File (*.csv)')[0]
        if fname != '':
            self.settings['pathdata'] = os.path.dirname(fname)
            self.save_settings()

        dataKey = os.path.basename(fname)
        dataVal = pd.read_csv(fname)

        self.data[dataKey] = dataVal
        self.gui.dataComboBox.addItem(dataKey, dataVal)
        self.update_data_table(dataKey)
        self.update_control(self.gui.plotXListWidget, dataVal.columns)
        self.update_control(self.gui.plotYListWidget, dataVal.columns)

    def update_data_table(self, key=None):
        key = key if key is not None else self.gui.dataComboBox.currentText()
        qt_helper.qtable_load_from_pandas(self.gui.dataTableWidget, self.data[key])

    def update_control(self, qComboBox, labels):
        qComboBox.clear()
        qComboBox.addItems(labels)

    def _react_datatable_dropdown_menu(self, point):
        self._explMenu = QtWidgets.QMenu(self.gui.dataTableWidget)
        actionConvertDateTime = self._explMenu.addAction('Column to DateTime')
        actionConvertDateTime.triggered.connect(self.data_convert_col_datetime)

        timeActions = []
        for timeType in self.timeFunctionDict.keys():
            timeActions += [self._explMenu.addAction('DateTime to ' + timeType)]
            timeActions[-1].triggered.connect(partial(self.data_parse_col_datetime, timeType))  #   self.timeMenuResponseDict[timeType]

        self._explMenu.popup(self.gui.dataTableWidget.viewport().mapToGlobal(point))

    def data_convert_col_datetime(self):
        selectedCols = qt_helper.qtable_get_selected_columns(self.gui.dataTableWidget)
        if len(selectedCols) != 1:
            self._warning("Must select exactly 1 row")
            return
        iCol = selectedCols[0]

        dataKey = self.gui.dataComboBox.currentText()
        self.data[dataKey][iCol] = pd.to_datetime(self.data[dataKey][iCol], infer_datetime_format=True)
        self.update_data_table()
        self.update_control(self.gui.plotXListWidget, self.data[dataKey].columns)
        self.update_control(self.gui.plotYListWidget, self.data[dataKey].columns)

    def data_parse_col_datetime(self, timeType):
        selectedCols = qt_helper.qtable_get_selected_columns(self.gui.dataTableWidget)
        if len(selectedCols) != 1:
            self._warning("Must select exactly 1 row")
            return
        iCol = selectedCols[0]

        dataKey = self.gui.dataComboBox.currentText()
        if timeType in self.timeFunctionDict.keys():
            timeFunc = self.timeFunctionDict[timeType]
            self.data[dataKey][iCol+'.'+timeType] = [timeFunc(t) for t in self.data[dataKey][iCol]]
        else:
            raise ValueError("Unexpected timeType", timeType)
        self.update_data_table()
        self.update_control(self.gui.plotXListWidget, self.data[dataKey].columns)
        self.update_control(self.gui.plotYListWidget, self.data[dataKey].columns)

    def plot_data(self):
        dataLabel = self.gui.dataComboBox.currentText()
        plotType = self.gui.plotTypeComboBox.currentText()
        labelsX = qt_helper.qlist_selected_labels(self.gui.plotXListWidget)
        labelsY = qt_helper.qlist_selected_labels(self.gui.plotYListWidget)

        if plotType in self.plotFunctions.keys():
            rez = self.plotFunctions[plotType](self.plotlayout.canvas.axes, labelsX, labelsY, dataLabel, self.data)
        else:
            self._warning("Unknown plot type", plotType)
            return

        if rez[0]:
            self._warning(rez[1])

        self.plotlayout.canvas.draw()
        self.plotlayout.canvas.flush_events()

    # React to key presses
    def key_press_event(self, e):
        if e.key() == QtCore.Qt.Key_Plus or e.key() == QtCore.Qt.Key_Minus:
            self.settings['fontsize'] += int(e.key() == QtCore.Qt.Key_Plus) - int(e.key() == QtCore.Qt.Key_Minus)
            self.save_settings()
            self.update_system_font_size()

    def update_system_font_size(self):
        print("New font size", self.settings['fontsize'])
        self.gui.centralWidget.setStyleSheet("font-size: " + str(self.settings['fontsize']) + "pt;")
        self.gui.menuBar.setStyleSheet("font-size: " + str(self.settings['fontsize']) + "pt;")


#######################################################
## Start the QT window
#######################################################
if __name__ == '__main__' :
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = QtWidgets.QMainWindow()
    locale.setlocale(locale.LC_TIME, "en_GB.utf8")
    classInstance = DataModelingGUI(mainwindow)
    mainwindow.show()
    sys.exit(app.exec_())
