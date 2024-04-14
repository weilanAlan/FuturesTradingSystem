# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'datadisplay.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1725, 1030)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 10, 226, 26))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_contract = QtWidgets.QLabel(self.layoutWidget)
        self.label_contract.setObjectName("label_contract")
        self.horizontalLayout.addWidget(self.label_contract)
        self.comboBox_contract = QtWidgets.QComboBox(self.layoutWidget)
        self.comboBox_contract.setObjectName("comboBox_contract")
        self.comboBox_contract.addItem("")
        self.comboBox_contract.addItem("")
        self.comboBox_contract.addItem("")
        self.comboBox_contract.addItem("")
        self.comboBox_contract.addItem("")
        self.comboBox_contract.addItem("")
        self.horizontalLayout.addWidget(self.comboBox_contract)
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(20, 160, 1681, 771))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout_kline_graph = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_kline_graph.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_kline_graph.setObjectName("verticalLayout_kline_graph")
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(20, 40, 1681, 111))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_dateframe = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_dateframe.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_dateframe.setObjectName("verticalLayout_dateframe")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1725, 30))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.action_dayK = QtWidgets.QAction(MainWindow)
        self.action_dayK.setObjectName("action_dayK")
        self.action_weekK = QtWidgets.QAction(MainWindow)
        self.action_weekK.setObjectName("action_weekK")
        self.action_monthK = QtWidgets.QAction(MainWindow)
        self.action_monthK.setObjectName("action_monthK")
        self.action_quarterK = QtWidgets.QAction(MainWindow)
        self.action_quarterK.setObjectName("action_quarterK")
        self.action_yearK = QtWidgets.QAction(MainWindow)
        self.action_yearK.setObjectName("action_yearK")
        self.action_1min = QtWidgets.QAction(MainWindow)
        self.action_1min.setObjectName("action_1min")
        self.action_3min = QtWidgets.QAction(MainWindow)
        self.action_3min.setObjectName("action_3min")
        self.action_5min = QtWidgets.QAction(MainWindow)
        self.action_5min.setObjectName("action_5min")
        self.action_10min = QtWidgets.QAction(MainWindow)
        self.action_10min.setObjectName("action_10min")
        self.action_15min = QtWidgets.QAction(MainWindow)
        self.action_15min.setObjectName("action_15min")
        self.action_30min = QtWidgets.QAction(MainWindow)
        self.action_30min.setObjectName("action_30min")
        self.action_1h = QtWidgets.QAction(MainWindow)
        self.action_1h.setObjectName("action_1h")
        self.action_2h = QtWidgets.QAction(MainWindow)
        self.action_2h.setObjectName("action_2h")
        self.toolBar.addAction(self.action_dayK)
        self.toolBar.addAction(self.action_weekK)
        self.toolBar.addAction(self.action_monthK)
        self.toolBar.addAction(self.action_quarterK)
        self.toolBar.addAction(self.action_yearK)
        self.toolBar.addAction(self.action_1min)
        self.toolBar.addAction(self.action_3min)
        self.toolBar.addAction(self.action_5min)
        self.toolBar.addAction(self.action_10min)
        self.toolBar.addAction(self.action_15min)
        self.toolBar.addAction(self.action_30min)
        self.toolBar.addAction(self.action_1h)
        self.toolBar.addAction(self.action_2h)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_contract.setText(_translate("MainWindow", "金融期货合约："))
        self.comboBox_contract.setItemText(0, _translate("MainWindow", "RB888"))
        self.comboBox_contract.setItemText(1, _translate("MainWindow", "RB99"))
        self.comboBox_contract.setItemText(2, _translate("MainWindow", "SA99"))
        self.comboBox_contract.setItemText(3, _translate("MainWindow", "SA888"))
        self.comboBox_contract.setItemText(4, _translate("MainWindow", "jm888"))
        self.comboBox_contract.setItemText(5, _translate("MainWindow", "jm99"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.action_dayK.setText(_translate("MainWindow", "日K"))
        self.action_weekK.setText(_translate("MainWindow", "周K"))
        self.action_monthK.setText(_translate("MainWindow", "月K"))
        self.action_quarterK.setText(_translate("MainWindow", "季K"))
        self.action_yearK.setText(_translate("MainWindow", "年K"))
        self.action_1min.setText(_translate("MainWindow", "1分"))
        self.action_3min.setText(_translate("MainWindow", "3分"))
        self.action_5min.setText(_translate("MainWindow", "5分"))
        self.action_5min.setToolTip(_translate("MainWindow", "5分"))
        self.action_10min.setText(_translate("MainWindow", "10分"))
        self.action_10min.setToolTip(_translate("MainWindow", "10分"))
        self.action_15min.setText(_translate("MainWindow", "15分"))
        self.action_15min.setToolTip(_translate("MainWindow", "15分"))
        self.action_30min.setText(_translate("MainWindow", "30分"))
        self.action_30min.setToolTip(_translate("MainWindow", "30分"))
        self.action_1h.setText(_translate("MainWindow", "1小时"))
        self.action_1h.setToolTip(_translate("MainWindow", "1小时"))
        self.action_2h.setText(_translate("MainWindow", "2小时"))
        self.action_2h.setToolTip(_translate("MainWindow", "2小时"))
